# Proprietary copyright: Clearpath Robotics, Confidential
#
# @author    Kieran Broekhoven <kbroekhoven@clearpathrobotics.com>
# @copyright (c) 2016, Clearpath Robotics, Inc., All rights reserved.

from __future__ import absolute_import

try: 
    VERSION = __import__('pkg_resources') \
        .get_distribution(__name__).version
except Exception, e:
    VERSION = 'unknown'
