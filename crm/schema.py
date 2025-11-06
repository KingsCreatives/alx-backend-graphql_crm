import graphene
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .schema_inputs import CreateCustomerInput, CreateOrderInput, CreateProductInput, BulkCustomerInput
from .filters import CustomerFilter, ProductFilter, OrderFilter
from .models import Customer, Product, Order
from .schema_types import CustomerType, ProductType, OrderType
from .utils import validate_phone, to_decimal




class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(customer=None, message="Failed to create customer.",
                                      errors=[f"Email '{input.email}' already exists."])
            validate_phone(input.phone)
            customer = Customer.objects.create(
                name=input.name.strip(),
                email=input.email.strip().lower(),
                phone=(input.phone.strip() if input.phone else None)
            )
            return CreateCustomer(customer=customer, message="Customer created successfully.", errors=[])
        except Exception as exc:
            return CreateCustomer(customer=None, message="Failed to create customer.", errors=[str(exc)])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(BulkCustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for idx, record in enumerate(input, start=1):
            try:
                name = (record.name or "").strip()
                email = (record.email or "").strip().lower()
                phone = (record.phone or None)
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Row {idx}: Email '{email}' already exists.")
                    continue
                validate_phone(phone)
                customer = Customer.objects.create(name=name, email=email, phone=phone)
                created_customers.append(customer)
            except Exception as exc:
                errors.append(f"Row {idx}: {str(exc)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            # Convert price to Decimal safely
            price = to_decimal(input.price)
            if price <= Decimal("0"):
                return CreateProduct(product=None, errors=["Price must be a positive number."])
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                return CreateProduct(product=None, errors=["Stock cannot be negative."])

            product = Product.objects.create(name=input.name.strip(), price=price, stock=stock)
            return CreateProduct(product=product, errors=[])
        except Exception as exc:
            return CreateProduct(product=None, errors=[str(exc)])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            # Validate customer
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                return CreateOrder(order=None, errors=[f"Customer with id '{input.customer_id}' does not exist."])

            # Validate product IDs list
            product_ids = list(input.product_ids) if input.product_ids else []
            if not product_ids:
                return CreateOrder(order=None, errors=["At least one product must be provided."])

            # Fetch products
            products_qs = Product.objects.filter(id__in=product_ids)
            found_ids = {str(p.id) for p in products_qs}
            missing_ids = [pid for pid in product_ids if str(pid) not in found_ids]
            if missing_ids:
                return CreateOrder(order=None, errors=[f"Invalid product IDs: {missing_ids}"])

            # Compute total_amount using Decimal arithmetic
            total_amount = sum((p.price for p in products_qs), Decimal("0.00"))

            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount,
                order_date=input.order_date or timezone.now()
            )
            order.products.set(products_qs)
            order.save()

            return CreateOrder(order=order, errors=[])
        except Exception as exc:
            return CreateOrder(order=None, errors=[str(exc)])

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        order = info.variable_values.get("orderBy")  
        
        if order:
            qs = qs.order_by(order)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        order = info.variable_values.get("orderBy")
        if order:
            qs = qs.order_by(order)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.select_related("customer").prefetch_related("products").all()
        order = info.variable_values.get("orderBy")
        if order:
            qs = qs.order_by(order)
        return qs



class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
