// Copyright (C) 2011-2018 ycmd contributors
//
// This file is part of ycmd.
//
// ycmd is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// ycmd is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with ycmd.  If not, see <http://www.gnu.org/licenses/>.

#include "TestUtils.h"

namespace YouCompleteMe {

namespace fs = boost::filesystem;

std::ostream& operator<<( std::ostream& os, const CodePointTuple &code_point ) {
  os << "{ " << PrintToString( code_point.normal_ ) << ", "
             << PrintToString( code_point.folded_case_ ) << ", "
             << PrintToString( code_point.swapped_case_ ) << ", "
             << PrintToString( code_point.is_letter_ ) << ", "
             << PrintToString( code_point.is_punctuation_ ) << ", "
             << PrintToString( code_point.is_uppercase_ ) << ", "
             << PrintToString( code_point.break_property_ ) << " }";
  return os;
}

std::ostream& operator<<( std::ostream& os, const CodePoint &code_point ) {
  os << CodePointTuple( code_point );
  return os;
}


std::ostream& operator<<( std::ostream& os, const CodePoint *code_point ) {
  os << "*" << *code_point;
  return os;
}


std::ostream& operator<<( std::ostream& os, const CharacterTuple &character ) {
  os << "{ " << PrintToString( character.normal_ ) << ", "
             << PrintToString( character.base_ ) << ", "
             << PrintToString( character.folded_case_ ) << ", "
             << PrintToString( character.swapped_case_ ) << ", "
             << PrintToString( character.is_base_ ) << ", "
             << PrintToString( character.is_letter_ ) << ", "
             << PrintToString( character.is_punctuation_ ) << ", "
             << PrintToString( character.is_uppercase_ ) << " }";
  return os;
}


std::ostream& operator<<( std::ostream& os, const Character &character ) {
  os << PrintToString( CharacterTuple( character ) );
  return os;
}


std::ostream& operator<<( std::ostream& os, const Character *character ) {
  os << "*" << *character;
  return os;
}


std::ostream& operator<<( std::ostream& os, const WordTuple &word ) {
  os << "{ " << PrintToString( word.text_ ) << ", "
             << PrintToString( word.characters_ ) << " }";
  return os;
}


std::ostream& operator<<( std::ostream& os, const Word &word ) {
  os << WordTuple( word );
  return os;
}


boost::filesystem::path PathToTestFile( const std::string &filepath ) {
  fs::path path_to_testdata = fs::current_path() / fs::path( "testdata" );
  return path_to_testdata / fs::path( filepath );
}

} // namespace YouCompleteMe
