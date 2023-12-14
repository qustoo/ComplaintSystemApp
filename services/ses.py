import boto3

from config import settings


class SESService:
    def __init__(self):
        self.key = settings.AWS_ACCESS_KEY
        self.secret = settings.AWS_SECRET_KEY
        self.ses = boto3.client(
            "ses",
            region_name=settings.AWS_REGION,
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
        )

    def send_mail(self, subject, to_addresses, text_data):
        body = {"Text": {"Data": text_data, "Charset": "UTF-8"}}

        self.ses.send_email(
            Source="test_email@gmail.com",
            Destination={
                "ToAddresses": to_addresses,
                "CcAddresses": [],
                "BccAddresses": [],
            },
            Message={"Subject": {"Data": subject, "Charset": "UTF-8"}, "Body": body},
        ),

ses = SESService()