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

def main():
    print("{:<20} {:<50} {:<15}".format('Region', 'Resource ID', 'Resource Type'))
    print("-" * 85)
    
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    for region in regions:
        session = boto3.Session(region_name=region)
        # List EC2 Instances
        resources = list_ec2_instances(session, region)
        # List S3 Buckets
        resources += list_s3_buckets(session, region)
        # List RDS Instances
        resources += list_rds_instances(session, region)
        # List Data Lakes (Glue Databases)
        resources += list_data_lakes(session, region)
        # List Lambda Functions
        resources += list_lambda_functions(session, region)

        if not resources:
            print(f"{region:<20} {'No resources found.':<50} {'N/A':<15}")
        else:
            for resource_id, resource_type in resources:
                print("{:<20} {:<50} {:<15}".format(region, resource_id, resource_type))

if __name__ == "__main__":
    main()
