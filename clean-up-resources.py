import boto3

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

def list_kms_keys(session, region):
    kms = session.client('kms')
    paginator = kms.get_paginator('list_keys')
    keys = []
    for page in paginator.paginate():
        keys.extend([(key['KeyId'], 'KMS Key') for key in page['Keys']])
    return keys

def main():
    print("{:<20} {:<50} {:<15}".format('Region', 'Resource ID', 'Resource Type'))
    print("-" * 85)
    
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    for region in regions:
        session = boto3.Session(region_name=region)
        resources = []
        resources += [(res_id, 'EC2 Instance') for res_id in list_ec2_instances(session, region)]
        resources += [(res_id, 'S3 Bucket') for res_id in list_s3_buckets(session, region)]
        resources += [(res_id, 'RDS Instance') for res_id in list_rds_instances(session, region)]
        resources += [(res_id, 'Data Lake (Glue Database)') for res_id in list_data_lakes(session, region)]
        resources += [(res_id, 'Lambda Function') for res_id in list_lambda_functions(session, region)]
        resources += list_kms_keys(session, region)

        if not resources:
            print(f"{region:<20} {'No resources found.':<50} {'N/A':<15}")
        else:
            for resource_id, resource_type in resources:
                print("{:<20} {:<50} {:<15}".format(region, resource_id, resource_type))
            confirm_and_delete(session, resources, region)

if __name__ == "__main__":
    main()
