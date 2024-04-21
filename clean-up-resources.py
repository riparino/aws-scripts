import boto3

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
            # Fetch the key details to check if it's an AWS-managed key
            key_details = kms.describe_key(KeyId=key['KeyId'])
            # Check if the key is customer-managed
            if key_details['KeyMetadata']['KeyManager'] == 'CUSTOMER':
                keys.append((key['KeyId'], 'KMS Key'))
    return keys

def delete_resource(session, resource_id, resource_type, region):
    if resource_type == 'EC2 Instance':
        ec2 = session.resource('ec2')
        instance = ec2.Instance(resource_id)
        instance.terminate()
        print(f'Terminated EC2 instance {resource_id} in {region}.')
    elif resource_type == 'S3 Bucket':
        s3 = session.resource('s3')
        bucket = s3.Bucket(resource_id)
        bucket.objects.all().delete()
        bucket.delete()
        print(f'Deleted S3 bucket {resource_id} in {region}.')
    elif resource_type == 'Lambda Function':
        lambda_client = session.client('lambda')
        lambda_client.delete_function(FunctionName=resource_id)
        print(f'Deleted Lambda function {resource_id} in {region}.')
    elif resource_type == 'Data Lake (Glue Database)':
        glue = session.client('glue')
        glue.delete_database(Name=resource_id)
        print(f'Deleted Data Lake (Glue Database) {resource_id} in {region}.')
    elif resource_type == 'RDS Instance':
        rds = session.client('rds')
        rds.delete_db_instance(DBInstanceIdentifier=resource_id, SkipFinalSnapshot=True)
        print(f'Deleted RDS instance {resource_id} in {region}.')
    elif resource_type == 'KMS Key':
        kms = session.client('kms')
        kms.schedule_key_deletion(KeyId=resource_id, PendingWindowInDays=7)
        print(f'Scheduled deletion for KMS Key {resource_id} in {region}.')

def confirm_and_delete(session, resources, region):
    for resource_id, resource_type in resources:
        response = input(f"Delete {resource_type} '{resource_id}' in {region}? (yes/no): ")
        if response.lower() == 'yes':
            delete_resource(session, resource_id, resource_type, region)
        else:
            print(f"Skipped {resource_type} '{resource_id}' in {region}.")

def main():
    print("{:<20} {:<50} {:<15}".format('Region', 'Resource ID', 'Resource Type'))
    print("-" * 85)
    
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

        if not resources:
            print(f"{region:<20} {'No resources found.':<50} {'N/A':<15}")
        else:
            for resource_id, resource_type in resources:
                print("{:<20} {:<50} {:<15}".format(region, resource_id, resource_type))
            confirm_and_delete(session, resources, region)

if __name__ == "__main__":
    main()
