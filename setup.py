#!/usr/bin/env python

#"Copyright 2009 Bryan Harris"
#
#This file is part of reduce.
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
setup(name='reduce',
      version='2.2.4',
      py_modules=['dataFile','reducePlot','measurementFile','tee'],
      scripts=['rlo.py'],
      description='A program for making pretty pictures of a whole directory test data at once.',
      author='Bryan W. Harris',
      author_email='brywilharris@gmail.com',
      license='GPL v3 or later',
      url='https://launchpad.net/reduce',
      long_description='A program for making pretty pictures of a whole directory test data at once.'
      )

