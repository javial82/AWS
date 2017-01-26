#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

"""Deletes ALL objects from a given bucket.
This script needs boto3: pip install boto3
"""

import sys
import argparse

import boto3


__version__ = "0.1"
__version__ = "0.1"
__title__ = "delete_bucket_content"
__author__ = "Xavier Alonso"
__email__ = "xavier.alonso@gmail.com"


def parser_args():
    """Function used to handle parameters and their descriptions"""
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        '-b', '--bucket', dest='bucket',
        help='Bucket we want to get empty.',
        required=True
    )
    parser.add_argument(
        '-m', '--max-keys', dest='maxkeys',
        help='Max keys to be listed on every api call.',
        required=False, default=123
    )
    return parser.parse_args()

class AWSConnect(object):
    """Class used to connect to AWS services"""

    def __init__(self, bucket, maxkeys):
        self.con = boto3.client('s3')
        self.bucket = bucket
        self.maxkeys = maxkeys
        self.unused = 0

    def delete_object(self):
        """Get a bucket objects list and use it to delete content."""
        total = 0
        while True:
            if not S3object(self.con, self.bucket).get_objects(self.maxkeys)[
                    'Contents'
            ]:
                break
            objects_iterator = iter(
                S3object(self.con, self.bucket).get_objects(self.maxkeys)[
                    'Contents'
                ]
            )
            for i in objects_iterator:
                print str(total) + ") Deleting object "+ i['Key']
                S3object(self.con, self.bucket).delete_object(i['Key'])
                total = total + 1
        return total


class S3object(object):
    """Class used to get objects list from a given S3 bucket and
    dekete them.
    """

    def __init__(self, connection, bucket):
        self.connection = connection
        self.bucket_to_empty = bucket

    def get_objects(self, maxkeys):
        """Return S3 bucket objects list."""
        return self.connection.list_objects(
            Bucket=self.bucket_to_empty, MaxKeys=maxkeys
        )

    def delete_object(self, key):
        """Delete a given object by its key"""
        self.connection.delete_object(Bucket=self.bucket_to_empty, Key=key)

def main():
    """Main function, it call necessary classes and methods"""

    args = parser_args()
    exit_code = 0
    con = AWSConnect(args.bucket, int(args.maxkeys))

    print "Deleted " + str(con.delete_object()) + " objects."

    return exit_code

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print 'Caught Control-C...'
        sys.exit(1)
