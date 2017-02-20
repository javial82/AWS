#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

"""Check reserved instances status. EC2 and RDS.
This script needs boto3 and pytz: pip install boto3 pytz
"""

import sys
import argparse
from datetime import datetime, timedelta

import boto3
from pytz import timezone


__version__ = "0.1"
__title__ = "check_reserved_instances"
__author__ = "Xavier Alonso"
__email__ = "javi.al@gmail.com"

EXPIRATION_DAYS = 60

def parser_args():
    """Function used to handle parameters and their descriptions"""
    parser = argparse.ArgumentParser(
        description='Get AWS reserved instances status.'
    )
    parser.add_argument(
        '-s', '--service', dest='service',
        help='Service to query about reserved instances. Values: ec2 or rds',
        required=True, choices=['ec2', 'rds']
    )
    parser.add_argument(
        '-r', '--region', dest='region',
        help='Choose AWS region', default='eu-west-q',
        required=True, choices=['eu-west-1']
    )
    parser.add_argument(
        '-u', '--usage', dest='usage',
        help='Returns the number of reservations that are not used.',
        action='store_true'
    )
    parser.add_argument(
        '-e', '--expiration', dest='expiration',
        help='Returns number of reservations that expire in next 30 days.',
        action='store_true'
    )

    return parser.parse_args()

class AWSConnect(object):
    """Class used to connect to different AWS services"""

    def __init__(self, service, region):
        self.service = service
        self.region = region
        self.con = boto3.client(self.service)
        self.unused = 0

    def get_usage(self):
        """Return the number of reserved instances aren't being used."""
        if self.service == 'ec2':
            reservations = Ec2(self.con).get_instances()['Reservations']
            reserved_instances = Ec2(self.con).get_reserved_instances()[
                'ReservedInstances'
            ]
            for i_reservations in reservations:
                for instance in i_reservations['Instances']:
                    for reserve in reserved_instances:
                        if reserve['State'] == 'active'\
                                and reserve['Scope'] == 'Region'\
                                and instance['InstanceType'] == reserve[
                                        'InstanceType'
                                ] and instance['State']['Name'] == 'running':
                            reserve['InstanceCount'] = reserve[
                                'InstanceCount'
                            ] - 1
            for reserve in reserved_instances:
                if reserve['State'] == 'active'\
                        and reserve['InstanceCount'] > 0:
                    self.unused = self.unused + reserve['InstanceCount']
        elif self.service == 'rds':
            dbinstances = Rds(self.con).get_dbinstances()['DBInstances']
            reserved_dbinstances = Rds(self.con).get_reserved_dbinstances()[
                'ReservedDBInstances'
            ]
            for instance in dbinstances:
                for reserve in reserved_dbinstances:
                    if reserve['State'] == 'active'\
                            and instance['DBInstanceClass'] == reserve[
                                    'DBInstanceClass'
                            ] and instance['MultiAZ'] == reserve['MultiAZ']\
                            and instance['Engine'] == reserve[
                                'ProductDescription'
                            ]:
                        reserve['DBInstanceCount'] = reserve[
                            'DBInstanceCount'
                        ] - 1
            for reserve in reserved_dbinstances:
                if reserve['State'] == 'active'\
                        and reserve['DBInstanceCount'] > 0:
                    self.unused = self.unused + reserve['DBInstanceCount']
        return self.unused

    def get_expiring(self):
        """Return the number of reserved instances are expiring
        in next EXPIRATION_DAYS constant value.
        """
        expiring = 0
        if self.service == 'ec2':
            reserved_instances = Ec2(self.con).get_reserved_instances()[
                'ReservedInstances'
            ]
            for reserve in reserved_instances:
                if reserve['End'] < datetime.now(tz=timezone('UTC'))\
                        + timedelta(EXPIRATION_DAYS):
                    expiring = expiring + 1
        elif self.service == 'rds':
            reserved_dbinstances = Rds(self.con).get_reserved_dbinstances()[
                'ReservedDBInstances'
            ]
            for reserve in reserved_dbinstances:
                if reserve['StartTime'] < datetime.now(tz=timezone('UTC'))\
                        - timedelta(365 - EXPIRATION_DAYS)\
                        and reserve['State'] == 'active':
                    expiring = expiring + 1
        return expiring

class Ec2(object):
    """Class used to get information from EC2 instances and
    reserved instances.
    """

    def __init__(self, connection):
        self.connection = connection

    def get_instances(self):
        """Return EC2 instances information."""
        return self.connection.describe_instances()

    def get_reserved_instances(self):
        """Return EC2 reserved instances information. Only the
        active ones.
        """
        return self.connection.describe_reserved_instances(
            Filters=[{'Name': 'state', 'Values': ['active']}]
        )

class Rds(object):
    """Class used to get information from RDS dbinstances and
    reserved dbinstances.
    """

    def __init__(self, connection):
        self.connection = connection

    def get_dbinstances(self):
        """Return RDS instances information."""
        return self.connection.describe_db_instances()

    def get_reserved_dbinstances(self):
        """Return RDS reserved instances information. All
        of them. Filter option is not functional at the moment of write this.
        """
        return self.connection.describe_reserved_db_instances()

def main():
    """Main function, it call necessary classes and methods"""

    args = parser_args()
    exit_code = 0
    con = AWSConnect(args.service, args.region)

    if args.usage:
        # Get EC2 or RDS usage
        print con.get_usage()
    elif args.expiration:
        # Get EC2 or RDS number of instances expiring before expiration_days
        print con.get_expiring()

    return exit_code

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print 'Caught Control-C...'
        sys.exit(1)
