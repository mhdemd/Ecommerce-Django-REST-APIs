
# Query Optimization

To ensure high performance and scalability of the RadinGalleryAPI, several query optimization techniques have been implemented. These optimizations minimize database load, reduce response times, and enhance the overall efficiency of the API endpoints. Below are the detailed strategies employed:

## 1. Efficient Database Queries

### a. `select_related`

**Purpose:**  
`select_related` is used for single-valued relationships (e.g., ForeignKey, OneToOneField) to perform SQL joins and retrieve related objects in a single query. This reduces the number of queries executed, especially when accessing related data.

**Implementation Example:**

```python
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).select_related("category", "brand")
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
```

**Explanation:**  
In the `ProductDetailView`, `select_related` fetches the related `category` and `brand` objects alongside the `Product` in a single database query. This avoids additional queries when accessing these related fields in the serializer or templates.

### b. `prefetch_related`

**Purpose:**  
`prefetch_related` is used for multi-valued relationships (e.g., ManyToManyField, reverse ForeignKey) to perform separate queries and efficiently fetch related objects. It is particularly useful for retrieving large sets of related data.

**Implementation Example:**

```python
class ProductInventoryListView(ListAPIView):
    serializer_class = ProductInventorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")
        queryset = (
            ProductInventory.objects.filter(product__id=product_id)
            .select_related("product")
            .prefetch_related(
                Prefetch(
                    "attribute_values",
                    queryset=ProductAttributeValue.objects.select_related("product_attribute"),
                )
            )
            .order_by("-created_at")
        )
        return queryset
```

**Explanation:**  
In the `ProductInventoryListView`, `prefetch_related` is used to fetch all related `attribute_values` for each `ProductInventory`. Additionally, `select_related` within the `Prefetch` ensures that each `ProductAttributeValue` fetches its related `product_attribute` in the same query. This approach minimizes the number of database hits when accessing related attribute values and their attributes.

## 2. Indexing and Ordering

**Purpose:**  
Applying appropriate indexing and ordering to frequently queried fields significantly speeds up data retrieval. Indexes allow the database to locate and access the data more efficiently.

**Implementation Example:**

```python
queryset = Media.objects.filter(
    product__id=product_id, product__is_active=True
).order_by("ordering")
```

**Explanation:**  
In the `ProductMediaListView`, the queryset filters `Media` objects based on `product_id` and `is_active` status. The `order_by("ordering")` ensures that the media items are retrieved in a specific order. By indexing the `product_id` and `ordering` fields in the `Media` model, these queries execute faster, especially when dealing with large datasets.

## 3. Pagination without Count

**Purpose:**  
Traditional pagination methods often require a `COUNT` query to determine the total number of records, which can be expensive for large datasets. Implementing custom pagination without relying on `COUNT` queries improves performance and reduces database load.

**Implementation Example:**

```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound

class NoCountPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            self.page_size = 10  # Default page size

        self.request = request
        self.page = None

        # Retrieve page number from query parameters, default to 1
        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            page_number = int(page_number)
            if page_number < 1:
                page_number = 1
        except (TypeError, ValueError):
            page_number = 1

        self.offset = (page_number - 1) * self.page_size
        self.limit = self.offset + self.page_size + 1  # Fetch one extra item to check for next page

        try:
            page = list(queryset[self.offset : self.limit])
        except Exception:
            raise NotFound("Invalid page.")

        if len(page) > self.page_size:
            self.has_next = True
            page = page[:self.page_size]
        else:
            self.has_next = False

        self.has_previous = self.offset > 0

        return page

    def get_paginated_response(self, data):
        return {
            "results": data,
            "previous": self.get_previous_link(),
            "next": self.get_next_link(),
        }
```

**Explanation:**  
The `NoCountPagination` class customizes the pagination behavior to avoid `COUNT` queries. It calculates the offset and limit based on the requested page number and page size. By fetching one extra item (`page_size + 1`), it determines whether there is a next page without performing a `COUNT`. The `has_next` and `has_previous` flags are set accordingly to manage navigation links.

## 4. Selective Data Retrieval

**Purpose:**  
Fetching only the necessary data reduces the payload size and improves response times. This involves selecting specific fields or limiting related data based on the API's requirements.

**Implementation Example:**

```python
queryset = ProductType.objects.all().order_by("name")
```

**Explanation:**  
In the `ProductTypeListView`, the queryset retrieves all `ProductType` objects ordered by their `name`. By selecting only the required fields and ordering appropriately, the API ensures that only pertinent data is sent to the client, optimizing both server performance and client-side processing.

## 5. Caching Strategies

**Purpose:**  
Caching frequently accessed data minimizes repeated database hits, thereby improving response times and reducing server load.

**Implementation Example:**

While not explicitly shown in the provided code, Redis is integrated into the project for caching purposes, such as storing user click counts, session data, and temporary tokens. Implementing Django's caching framework with Redis can significantly enhance performance.

**Example Configuration:**

```python
# settings.py

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

**Usage in Views or Serializers:**

```python
from django.core.cache import cache

def get_cached_data(key):
    data = cache.get(key)
    if not data:
        data = expensive_database_query()
        cache.set(key, data, timeout=300)  # Cache for 5 minutes
    return data
```

**Explanation:**  
By configuring Django to use Redis as the caching backend, the application can store and retrieve cached data efficiently. This setup is beneficial for data that doesn't change frequently, such as product listings or category information, ensuring faster response times and reduced database load.

## Summary

The combination of `select_related`, `prefetch_related`, strategic indexing and ordering, custom pagination without count, selective data retrieval, and effective caching strategies collectively enhance the performance and scalability of the RadinGalleryAPI. These optimizations ensure that the API can handle high traffic and large datasets efficiently, providing a seamless experience for end-users.

For further details on specific implementations or to contribute to the optimization strategies, please refer to the project's documentation or contact the development team.
