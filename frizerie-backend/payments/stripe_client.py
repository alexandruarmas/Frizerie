import stripe
from config.settings import get_settings

settings = get_settings()

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeClient:
    def __init__(self):
        self.stripe = stripe

    async def create_payment_intent(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        metadata: dict = None
    ) -> dict:
        """
        Create a payment intent with Stripe.
        
        Args:
            amount: Payment amount in smallest currency unit (e.g., cents)
            currency: Currency code (e.g., 'usd')
            payment_method: Payment method ID
            metadata: Additional metadata for the payment intent
        
        Returns:
            dict: Payment intent object
        """
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method,
                confirm=True,
                metadata=metadata or {},
                return_url=settings.STRIPE_RETURN_URL
            )
            return intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def retrieve_payment_intent(self, payment_intent_id: str) -> dict:
        """
        Retrieve a payment intent from Stripe.
        
        Args:
            payment_intent_id: Stripe payment intent ID
        
        Returns:
            dict: Payment intent object
        """
        try:
            return self.stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def create_refund(
        self,
        payment_intent_id: str,
        amount: float = None,
        reason: str = None
    ) -> dict:
        """
        Create a refund for a payment.
        
        Args:
            payment_intent_id: Stripe payment intent ID
            amount: Amount to refund (optional, defaults to full amount)
            reason: Reason for refund (optional)
        
        Returns:
            dict: Refund object
        """
        try:
            refund_params = {
                "payment_intent": payment_intent_id,
            }
            
            if amount:
                refund_params["amount"] = int(amount * 100)  # Convert to cents
            
            if reason:
                refund_params["reason"] = reason
            
            return self.stripe.Refund.create(**refund_params)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def validate_payment_method(self, payment_method_id: str) -> bool:
        """
        Validate a payment method.
        
        Args:
            payment_method_id: Stripe payment method ID
        
        Returns:
            bool: True if payment method is valid, False otherwise
        """
        try:
            self.stripe.PaymentMethod.retrieve(payment_method_id)
            return True
        except stripe.error.StripeError:
            return False

# Create a singleton instance
stripe_client = StripeClient() 