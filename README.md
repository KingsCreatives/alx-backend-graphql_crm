
---

# ALX Backend GraphQL CRM

This project is part of the **ALX Backend Specialization**. It focuses on building a simple **CRM system** using **GraphQL** and **Django**.
The system manages **customers**, **products**, and **orders**, with features like filtering, validation, and bulk creation.

---

## 🧩 Tasks Summary

### Task 0 – Setting Up GraphQL Schema

* Created models for Customer, Product, and Order.
* Defined `DjangoObjectType` classes for each model.
* Connected GraphQL to Django using `graphene-django`.

**What I learned:** How to expose Django models through GraphQL types.

---

### Task 1 – Implementing Mutations

* Added mutations to create customers, products, and orders.
* Used input types for structured data.
* Added validation for phone numbers and decimal fields.

**What I learned:** How to create and validate GraphQL mutations.

---

### Task 2 – Bulk Customer Creation

* Implemented a bulk mutation to add multiple customers at once.
* Handled errors for invalid rows.
* Used transactions to keep data consistent.

**What I learned:** How to perform bulk operations safely in GraphQL.

---

### Task 3 – Filtering and Querying

* Added filters for customers, products, and orders.
* Allowed ordering and flexible query options using `DjangoFilterConnectionField`.

**What I learned:** How to add filtering and sorting to GraphQL queries.

---

### Task 4 – Database Seeding

* Created a `seed_db.py` script to populate the database with sample data.
* Tested all queries and mutations using GraphiQL.

**What I learned:** How to seed a database for testing.

---

## ⚙️ Example Queries

**Create Customer**

```graphql
mutation {
  createCustomer(input: {
    name: "John Doe",
    email: "john@example.com",
    phone: "+233554000111"
  }) {
    customer { id name email phone }
    message
    errors
  }
}
```

**Filter Customers**

```graphql
{
  allCustomers(name_Icontains: "john") {
    edges {
      node {
        id
        name
        email
      }
    }
  }
}
```

---

## 🚀 Key Takeaways

* Learned how to build and connect a GraphQL API with Django.
* Gained skills in input validation, bulk operations, and filtering.
* Improved debugging and backend development experience.

---

## 🧑‍💻 Tech Stack

* Django
* Graphene-Django
* SQLite
* Python 3

---

