import boto3

def delete_ec2_instances(region):
    session = boto3.Session(region_name=region)
    ec2 = session.resource('ec2')
    for instance in ec2.instances.all():
        instance.terminate()
        print(f'Terminated EC2 instance {instance.id} in {region}')

def delete_s3_buckets(region):
    session = boto3.Session(region_name=region)
    s3 = session.client('s3')
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        try:
            s3_resource = session.resource('s3')
            bucket = s3_resource.Bucket(bucket['Name'])
            bucket.objects.all().delete()
            bucket.delete()
            print(f'Deleted S3 bucket {bucket.name} in {region}')
        except Exception as e:
            print(f"Error deleting S3 bucket {bucket['Name']} in {region}: {e}")

def main():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    for region in regions:
        print(f"Processing region: {region}")
        delete_ec2_instances(region)
        delete_s3_buckets(region)

if __name__ == "__main__":
    main()
