from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment


class PayPalClient:
    def __init__(self):
        self.client_id = "AVXCU_vK1UIfRqLh8-rtPvMZmW1ktL1EJWQMDw8-yFvxo5FIZbm8WXH5UTameESlYUxDQ4B6hpTb2KzV"
        self.client_secret = "EF8km3pE4i5pCVbOfnZ28Vlyu_8CMCfpR-jEVvzIVdTAJp2gG7ydqYZ24UR5Nzbjv8zJmbTk9hcbjA7d"
        self.environment = SandboxEnvironment(
            client_id=self.client_id, client_secret=self.client_secret
        )
        self.client = PayPalHttpClient(self.environment)


# Sandbox personal account info
# Email: sb-ugb3k28156761@personal.example.com
# Password: .@1cxPT&
