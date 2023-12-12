import json
import uuid
from fastapi import HTTPException
from config import settings
import requests


class WiseService:
    def __init__(self):
        self.main_url = settings.WISE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.WISE_TOKEN}",
        }
        profile_id = self._get_profile_id()
        self.profile_id = profile_id

    def _get_profile_id(self):
        url = self.main_url + "/v1/profiles"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            resp = resp.json()
            return [item["id"] for item in resp if item["type"] == "personal"][0]
        else:
            raise HTTPException(
                status_code=500,
                detail="Payment provider is not available at the moment",
            )

    def create_quote(self, amount):
        url = self.main_url + "/v2/quotes"
        data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "targetAmount": amount,
            "profile": self.profile_id,
        }
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        else:
            print(resp)
            raise HTTPException(
                status_code=500,
                detail="Payment provider is not available at the moment",
            )

    def create_recipient_account(self, full_name, iban):
        url = self.main_url + "/v1/accounts"
        data = {
            "currency": "EUR",
            "type": "iban",
            "profile": self.profile_id,
            "accountHolderName": full_name,
            "legalType": "PRIVATE",
            "details": {"iban": iban},
        }
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        else:
            print(resp)
            raise HTTPException(
                status_code=500,
                detail="Payment provider is not available at the moment",
            )

    def create_transfer(self, target_account_id, quote_id):
        customer_transaction_id = str(uuid.uuid4())
        url = self.main_url + "/v1/transfers"
        data = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_id,
            "customerTransactionId": customer_transaction_id,
            "details": {},
        }
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        else:
            print(resp)
            raise HTTPException(
                status_code=500,
                detail="Payment provider is not available at the moment",
            )

    def fund_transfer(self, transfer_id):
        url = (
            self.main_url
            + f"/v3/profiles/{self.profile_id}/transfers/{transfer_id}/payments"
        )
        data = {"type": "BALANCE"}
        resp = requests.post(url, data=json.dumps(data), headers=self.headers)
        if resp.status_code == 201:
            resp = resp.json()
            return resp["id"]
        else:
            print(resp)
            raise HTTPException(
                status_code=500, detail="Payment provider is notavailable at the moment"
            )

    def cancel_funds(self, transfer_id):
        url = self.main_url + f"/v1/transfers/{transfer_id}/cancel"
        resp = requests.put(url, headers=self.headers)

        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        print(resp)
        raise HTTPException(500, "Payment provider is not available at the moment")

wise = WiseService()
