# Copyright (C) 2013 Stanislav Golovanov <stgolovanov@gmail.com>
#                    Google Inc.
#
# This file is part of ycmd.
#
# ycmd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ycmd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ycmd.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# Not installing aliases from python-future; it's unreliable and slow.
from builtins import *  # noqa

import logging
import os
import re
from collections import defaultdict

from ycmd.completers.completer import Completer
from ycmd.utils import ( ExpandVariablesInPath, GetCurrentDirectory, OnWindows,
                         ToUnicode )
from ycmd import responses

EXTRA_INFO_MAP = { 1 : '[File]', 2 : '[Dir]', 3 : '[File&Dir]' }

_logger = logging.getLogger( __name__ )


class FilenameCompleter( Completer ):
  """
  General completer that provides filename and filepath completions.
  """

  def __init__( self, user_options ):
    super( FilenameCompleter, self ).__init__( user_options )

    # On Windows, backslashes are also valid path separators.
    self._triggers = [ '/', '\\' ] if OnWindows() else [ '/' ]

    self._path_regex = re.compile( """
      # Head part
      (?:
        # 'D:/'-like token
        [A-z]+:[%(sep)s]|

        # '/', './', '../', or '~'
        \.{0,2}[%(sep)s]|~|

        # '$var/'
        \$[A-Za-z0-9{}_]+[%(sep)s]
      )+

      # Tail part
      (?:
        # any alphanumeric, symbol or space literal
        [ %(sep)sa-zA-Z0-9(){}$+_~.\x80-\xff-\[\]]|

        # skip any special symbols
        [^\x20-\x7E]|

        # backslash and 1 char after it
        \\.
      )*$
      """ % { 'sep': '/\\\\' if OnWindows() else '/' }, re.X )


  def ShouldUseNowInner( self, request_data ):
    current_line = request_data[ 'line_value' ]
    start_codepoint = request_data[ 'start_codepoint' ]

    # inspect the previous 'character' from the start column to find the trigger
    # note: 1-based still. we subtract 1 when indexing into current_line
    trigger_codepoint = start_codepoint - 1

    return ( trigger_codepoint > 0 and
             current_line[ trigger_codepoint - 1 ] in self._triggers )


  def SupportedFiletypes( self ):
    return []


  def ComputeCandidatesInner( self, request_data ):
    current_line = request_data[ 'line_value' ]
    start_codepoint = request_data[ 'start_codepoint' ] - 1
    filepath = request_data[ 'filepath' ]
    line = current_line[ : start_codepoint ]

    path_match = self._path_regex.search( line )
    path_dir = ExpandVariablesInPath( path_match.group() ) if path_match else ''

    # If the client supplied its working directory, use that instead of the
    # working directory of ycmd
    working_dir = request_data.get( 'working_dir' )

    return GenerateCandidatesForPaths(
      _GetAbsolutePaths(
        path_dir,
        self.user_options[ 'filepath_completion_use_working_dir' ],
        filepath,
        working_dir) )


def _GetAbsolutePathForCompletions( path_dir,
                                    use_working_dir,
                                    filepath,
                                    working_dir ):
  """
  Returns the absolute path for which completion suggestions should be returned
  (in the standard case).
  """

  if os.path.isabs( path_dir ):
    # This is already an absolute path, return it
    return path_dir
  elif use_working_dir:
    # Return paths relative to the working directory of the client, if
    # supplied, otherwise relative to the current working directory of this
    # process
    if working_dir:
      return os.path.join( working_dir, path_dir )
    else:
      return os.path.join( GetCurrentDirectory(), path_dir )
  else:
    # Return paths relative to the file
    return os.path.join( os.path.join( os.path.dirname( filepath ) ),
                         path_dir )


def _GetAbsolutePaths( path_dir, use_working_dir, filepath, working_dir ):
  absolute_path_dir = _GetAbsolutePathForCompletions( path_dir,
                                                      use_working_dir,
                                                      filepath,
                                                      working_dir )

  try:
    # We need to pass a unicode string to get unicode strings out of
    # listdir.
    relative_paths = os.listdir( ToUnicode( absolute_path_dir ) )
  except Exception:
    _logger.exception( 'Error while listing %s folder.', absolute_path_dir )
    relative_paths = []

  return ( os.path.join( absolute_path_dir, relative_path )
           for relative_path in relative_paths )


def GenerateCandidatesForPaths( absolute_paths ):
  extra_info = defaultdict( int )
  basenames = []
  for absolute_path in absolute_paths:
    basename = os.path.basename( absolute_path )
    if extra_info[ basename ] == 0:
      basenames.append( basename )
    is_dir = os.path.isdir( absolute_path )
    extra_info[ basename ] |= ( 2 if is_dir else 1 )

  completion_dicts = []
  # Keep original ordering
  for basename in basenames:
    completion_dicts.append(
      responses.BuildCompletionData(
        basename,
        EXTRA_INFO_MAP[ extra_info[ basename ] ] ) )

  return completion_dicts
