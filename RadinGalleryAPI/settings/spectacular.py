SPECTACULAR_SETTINGS = {
    "TITLE": "my-APIs",
    "DESCRIPTION": "This is the API documentation for 'Ecommerce-Django-REST-APIs'.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "POSTPROCESSING_HOOKS": [
        "RadinGalleryAPI.utils.remove_empty_tags",  # Call the function to clean empty tags
    ],
    "TAGS": [
        # Authentication Group
        {
            "name": "Auth - Registration",
            "description": "Endpoints related to user registration and email verification.",
        },
        {
            "name": "Auth - Token",
            "description": "Endpoints related to obtaining, refreshing, and verifying JWT tokens.",
        },
        {
            "name": "Auth - Logout",
            "description": "Endpoints for user logout operations.",
        },
        {
            "name": "Auth - Password",
            "description": "Endpoints for managing user passwords, including reset and change.",
        },
        {
            "name": "Auth - Profile",
            "description": "Endpoints for fetching and updating user profile information.",
        },
        {
            "name": "Auth - OTP",
            "description": "Endpoints for managing two-factor authentication (2FA), including OTP generation and verification.",
        },
        {
            "name": "Auth - Session",
            "description": "Endpoints for managing user sessions, including session listing, deletion, and logout of all sessions.",
        },
        # Products Group
        {
            "name": "Product - List",
            "description": "Endpoints for listing products and retrieving product details.",
        },
        {
            "name": "Product - Media",
            "description": "Endpoints for managing product media, such as images and videos.",
        },
        {
            "name": "Product - Inventory",
            "description": "Endpoints for managing product inventory information.",
        },
        {
            "name": "Product - Types",
            "description": "Endpoints for managing product types and their details.",
        },
        {
            "name": "Product - Attributes",
            "description": "Endpoints for managing product attributes and their values.",
        },
        # Products Admin Group
        {
            "name": "Admin - Product",
            "description": "Admin endpoints for managing products and their details.",
        },
        {
            "name": "Admin - Product Media",
            "description": "Admin endpoints for managing product media such as images and videos.",
        },
        {
            "name": "Admin - Product Inventory",
            "description": "Admin endpoints for managing product inventory.",
        },
        {
            "name": "Admin - Product Types",
            "description": "Admin endpoints for managing product types.",
        },
        {
            "name": "Admin - Product Attributes",
            "description": "Admin endpoints for managing product attributes and their values.",
        },
        # Category Group
        {
            "name": "Category - List",
            "description": "Endpoints for listing all active categories accessible to users.",
        },
        {
            "name": "Category - Detail",
            "description": "Endpoint for retrieving the details of a single active category by pk.",
        },
        {
            "name": "Admin - Category",
            "description": "Admin endpoints for managing categories, including listing, creating, updating, and deleting categories.",
        },
        # Brand Group
        {
            "name": "Brand - List",
            "description": "Endpoints for listing brands accessible to users with filtering, searching, and ordering capabilities.",
        },
        {
            "name": "Brand - Detail",
            "description": "Endpoint for retrieving the details of a specific brand.",
        },
        {
            "name": "Admin - Brand",
            "description": "Admin endpoints for managing brands, including listing, creating, updating, and deleting brands.",
        },
    ],
}
