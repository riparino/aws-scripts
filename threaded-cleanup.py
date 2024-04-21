import boto3
import threading

def list_ec2_instances(session, region):
    ec2 = session.resource('ec2')
    instances = ec2.instances.all()
    return [(instance.id, 'EC2 Instance') for instance in instances]

def list_s3_buckets(session, region):
    s3 = session.client('s3')
    response = s3.list_buckets()
    return [(bucket['Name'], 'S3 Bucket') for bucket in response['Buckets']]

def list_rds_instances(session, region):
    rds = session.client('rds')
    response = rds.describe_db_instances()
    return [(db['DBInstanceIdentifier'], 'RDS Instance') for db in response['DBInstances']]

def list_data_lakes(session, region):
    glue = session.client('glue')
    response = glue.get_databases()
    return [(db['Name'], 'Data Lake (Glue Database)') for db in response['DatabaseList']]

def list_lambda_functions(session, region):
    lambda_client = session.client('lambda')
    response = lambda_client.list_functions()
    return [(function['FunctionName'], 'Lambda Function') for function in response['Functions']]

def list_kms_keys(session, region):
    kms = session.client('kms')
    paginator = kms.get_paginator('list_keys')
    keys = []
    for page in paginator.paginate():
        for key in page['Keys']:
            key_details = kms.describe_key(KeyId=key['KeyId'])
            if key_details['KeyMetadata']['KeyManager'] == 'CUSTOMER':
                keys.append((key['KeyId'], 'KMS Key'))
    return keys

def delete_resource(session, resource_id, resource_type, region, deletion_status):
    try:
        if resource_type == 'EC2 Instance':
            ec2 = session.resource('ec2')
            instance = ec2.Instance(resource_id)
            instance.terminate()
            deletion_status[resource_id] = 'Deleted'
        # Continue for other resource types...
    except Exception as e:
        deletion_status[resource_id] = f'Error: {str(e)}'

def main():
    print("Do you want to delete all deletable resources? (yes/no)")
    global_decision = input().lower() == 'yes'
    print("{:<20} {:<50} {:<15} {:<10}".format('Region', 'Resource ID', 'Resource Type', 'Deleted'))
    print("-" * 95)

    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    for region in regions:
        session = boto3.Session(region_name=region)
        resources = []
        resources += list_ec2_instances(session, region)
        resources += list_s3_buckets(session, region)
        resources += list_rds_instances(session, region)
        resources += list_data_lakes(session, region)
        resources += list_lambda_functions(session, region)
        resources += list_kms_keys(session, region)

        deletion_status = {}

        if not resources:
            print(f"{region:<20} {'No resources found.':<50} {'N/A':<15} {'N/A':<10}")
        else:
            threads = []
            for resource_id, resource_type in resources:
                if global_decision:
                    t = threading.Thread(target=delete_resource, args=(session, resource_id, resource_type, region, deletion_status))
                    t.start()
                    threads.append(t)
                print("{:<20} {:<50} {:<15} {:<10}".format(region, resource_id, resource_type, deletion_status.get(resource_id, 'Not Deleted')))
            for t in threads:
                t.join()  # Ensure all threads have completed

if __name__ == "__main__":
    main()
