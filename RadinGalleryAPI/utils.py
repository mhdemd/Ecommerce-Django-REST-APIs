def remove_empty_tags(result, generator, request, public):
    """
    Remove empty tags that do not have any associated paths in the schema.
    """
    if "tags" in result:
        # Collect tags that are actually used in the paths
        used_tags = set()
        for path_data in result.get("paths", {}).values():
            for method_data in path_data.values():
                if "tags" in method_data:
                    used_tags.update(method_data["tags"])

        # Keep only the tags that are used
        result["tags"] = [tag for tag in result["tags"] if tag["name"] in used_tags]

    return result
