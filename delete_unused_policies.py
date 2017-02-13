#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

"""Deletes ALL IAM unused policies an their versions.
This script needs boto3: pip install boto3
"""

import sys
import argparse

import boto3


__version__ = "0.1"
__title__ = "delete_unused_policies"
__author__ = "Xavier Alonso"
__email__ = "javi.al@gmail.com"


def parser_args():
    """Function used to handle parameters and their descriptions"""
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        '-n', '--noop', dest='noop',
        help='If you want to execute only to view what policies are affected.',
        required=False, action='store_true', default=False
    )
    return parser.parse_args()

class AWSConnect(object):
    """Class used to connect to AWS IAM an delete policies"""

    def __init__(self):
        self.con = boto3.client('iam')
        self.policies = {}
        self.policy_versions = {}

    def list_policies(self):
        """Return a list of the local policies"""
        return self.con.list_policies(
            Scope='Local'
        )

    def delete_unused(self, mode):
        """Delete unused local policies and their versions"""
        self.policies = self.list_policies()
        for policy in self.policies['Policies']:
            if policy['AttachmentCount'] < 1:
                self.policy_versions = self.con.list_policy_versions(
                    PolicyArn=policy['Arn']
                )
                for version in self.policy_versions['Versions']:
                    if not version['IsDefaultVersion']:
                        if not mode:
                            self.con.delete_policy_version(
                                PolicyArn=policy['Arn'],
                                VersionId=version['VersionId']
                            )
                        print policy['Arn'] + " - " + version['VersionId'] + \
                              " DELETED"
                if not mode:
                    self.con.delete_policy(
                        PolicyArn=policy['Arn']
                    )
                print policy['PolicyName'] + " DELETED"


def main():
    """Main function, it call necessary classes and methods"""

    args = parser_args()
    exit_code = 0
    con = AWSConnect()

    con.delete_unused(args.noop)

    return exit_code

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print 'Caught Control-C...'
        sys.exit(1)
