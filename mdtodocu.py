#!/usr/bin/env python3

import os
import re
import shutil
import json
import sys

def parse_summary(summary_path):
    """
    Parse the SUMMARY.md file and extract the hierarchy based on indentation levels.
    Returns a list of tuples (indentation level, filename, title, position).
    """
    with open(summary_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    hierarchy = []
    for position, line in enumerate(lines, start=1):  # Start counting from 1
        # Match lines like "- [File 1](path/to/filename.md)"
        match = re.match(r'^(\s*)- \[(.*?)\]\((.*\.md)\)', line)
        if match:
            indentation = len(match.group(1))  # Number of spaces for indentation
            title = match.group(2).strip()  # Extract title
            filename = os.path.basename(match.group(3)).strip()  # Extract filename and remove extra spaces
            hierarchy.append((indentation, filename, title, position))

    return hierarchy

def find_source_file(filename, search_dir):
    """
    Recursively search for a file with the given filename in the search directory.
    Returns the full path to the file if found, otherwise None.
    """
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.lower() == filename.lower():  # Case-insensitive comparison
                return os.path.join(root, file)
    return None

def generate_frontmatter(title, position):
    """
    Generate the frontmatter block for a markdown file.
    """
    return f"""---
title: "{title}"
sidebar_position: {position}
---\n\n"""

def create_category_json(directory, label, position):
    """
    Create a _category_.json file in the specified directory.
    """
    category_data = {
        "label": label,
        "position": position
    }
    category_path = os.path.join(directory, "_category_.json")
    with open(category_path, 'w', encoding='utf-8') as file:
        json.dump(category_data, file, indent=2)
    print(f"Created: {category_path}")

def extract_image_paths(markdown_content):
    """
    Extract image paths from markdown content.
    Returns a list of image paths.
    """
    # Regex to match markdown image syntax: ![alt text](path/to/image.png)
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
    return image_pattern.findall(markdown_content)

def find_image_in_directory(image_name, search_dir):
    """
    Recursively search for an image file in the directory.
    Returns the full path to the image if found, otherwise None.
    """
    # Normalize the image name to handle .jpg vs .jpeg
    image_name_without_ext, ext = os.path.splitext(image_name)
    valid_extensions = [ext, '.jpg', '.jpeg', '.png']  # Add other extensions if needed

    for root, _, files in os.walk(search_dir):
        for file in files:
            file_without_ext, file_ext = os.path.splitext(file)
            if file_without_ext.lower() == image_name_without_ext.lower() and file_ext.lower() in valid_extensions:
                return os.path.join(root, file)
    return None

def update_image_paths(markdown_content):
    """
    Update image paths in markdown content to use `./img/` prefix.
    """
    # Regex to match markdown image syntax: ![alt text](path/to/image.png)
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    def replace_image_path(match):
        image_path = match.group(1)
        # Extract the image filename
        image_name = os.path.basename(image_path)
        # Update the path to use `./img/`
        return f"![](./img/{image_name})"

    # Replace all image paths in the markdown content
    updated_content = image_pattern.sub(replace_image_path, markdown_content)
    return updated_content

def copy_images_to_destination(markdown_path, image_paths, output_dir, search_dir):
    """
    Copy images referenced in a markdown file to the correct directory.
    """
    # Get the directory of the markdown file in the output directory
    markdown_dir = os.path.dirname(markdown_path)
    img_dir = os.path.join(markdown_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    # Get the directory of the source markdown file
    source_markdown_dir = os.path.dirname(find_source_file(os.path.basename(markdown_path), search_dir))

    # Copy each image to the img directory
    for image_path in image_paths:
        # Extract the image filename
        image_name = os.path.basename(image_path)

        # Search for the image in the source directory
        source_image_path = find_image_in_directory(image_name, source_markdown_dir)
        
        if not source_image_path:
            # If not found in the same directory, search recursively in the entire source directory
            source_image_path = find_image_in_directory(image_name, search_dir)

        if source_image_path:
            # Construct the full destination path
            destination_image_path = os.path.join(img_dir, os.path.basename(source_image_path))

            # Normalize paths to avoid SameFileError
            source_image_path = os.path.normpath(source_image_path)
            destination_image_path = os.path.normpath(destination_image_path)

            # Check if source and destination are the same file
            if os.path.abspath(source_image_path) == os.path.abspath(destination_image_path):
                print(f"Skipping: Source and destination are the same file: {source_image_path}")
                continue

            # Copy the image
            shutil.copy(source_image_path, destination_image_path)
            print(f"Copied image: {source_image_path} -> {destination_image_path}")
        else:
            print(f"Warning: Image '{image_name}' not found in source directory. Skipping.")
            
def verify_images_in_markdown(output_dir, search_dir):
    """
    Verify that all images referenced in markdown files exist in the ./img directory.
    If not, search for them recursively in the source directory and log missing images.
    """
    log_file = "mdtodocu.log"
    missing_images = []

    # Walk through the output directory to find all markdown files
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".md"):
                markdown_path = os.path.join(root, file)
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract image paths from the markdown content
                image_paths = extract_image_paths(content)
                for image_path in image_paths:
                    # Extract the image filename
                    image_name = os.path.basename(image_path)

                    # Check if the image exists in the ./img directory
                    img_dir = os.path.join(os.path.dirname(markdown_path), "img")
                    image_file = os.path.join(img_dir, image_name)

                    if not os.path.exists(image_file):
                        # If not found, search for the image recursively in the source directory
                        source_image_path = find_image_in_directory(image_name, search_dir)
                        if source_image_path:
                            # Copy the image to the ./img directory
                            shutil.copy(source_image_path, image_file)
                            print(f"Found and copied missing image: {source_image_path} -> {image_file}")
                        else:
                            # Log the missing image
                            missing_images.append(image_name)
                            print(f"Missing image: {image_name}")

    # Write missing images to the log file
    if missing_images:
        with open(log_file, 'w', encoding='utf-8') as log:
            for image_name in missing_images:
                log.write(f'Image "{image_name}" cannot be found.\n')
        print(f"Logged missing images to {log_file}")

def process_include_statements(markdown_content, search_dir):
    """
    Process include statements in the markdown content.
    Replace the include statement with the content of the referenced file.
    Supports both direct file references and collection-based references (e.g., 'tech:mycelium0.md').
    """
    # Regex to match include statements:
    # !!wiki.include page:filename or !!wiki.include page:'collection:filename' or !!wiki.include page:'filename'
    include_pattern = re.compile(r"!!wiki\.include page:(?:'([^:]+):([^']+)'|'([^']+)'|([^\s]+))")

    def replace_include(match):
        # Check if the include statement uses the collection format (e.g., 'tech:mycelium0.md')
        if match.group(1) and match.group(2):
            collection = match.group(1)  # Collection name (e.g., 'tech')
            include_filename = match.group(2)  # Filename (e.g., 'mycelium0.md')
        elif match.group(3):
            # Direct file reference with single quotes (e.g., 'internet_archtecture0.md')
            collection = None
            include_filename = match.group(3)
        else:
            # Direct file reference without single quotes (e.g., 'mycelium0.md')
            collection = None
            include_filename = match.group(4)

        # Ensure the filename has the .md extension
        if not include_filename.endswith('.md'):
            include_filename += '.md'

        # Determine the directory to search based on the collection
        if collection:
            # Search in the collection directory (e.g., './tech/')
            collection_dir = os.path.join(search_dir, collection)
            included_file_path = find_source_file(include_filename, collection_dir)
        else:
            # Search recursively in the main directory
            included_file_path = find_source_file(include_filename, search_dir)

        if included_file_path:
            with open(included_file_path, 'r', encoding='utf-8') as included_file:
                return included_file.read()
        else:
            print(f"Warning: Included file '{include_filename}' not found in collection '{collection}'. Skipping.")
            return match.group(0)  # Return the original include statement if file not found

    # Replace all include statements in the markdown content
    processed_content = include_pattern.sub(replace_include, markdown_content)
    return processed_content

def create_directory_structure(hierarchy, search_dir, output_dir):
    """
    Create the directory structure based on the hierarchy, copy files, add frontmatter,
    create _category_.json files for directories, and handle images.
    """
    current_level = 0
    current_path = output_dir

    # Track which files have children
    has_children = set()
    for i, (indentation, filename, title, position) in enumerate(hierarchy):
        level = indentation // 2
        if i + 1 < len(hierarchy):
            next_level = hierarchy[i + 1][0] // 2
            if next_level > level:
                has_children.add(filename)

    for indentation, filename, title, position in hierarchy:
        # Calculate the level based on indentation (assuming 2 spaces per level)
        level = indentation // 2

        # Adjust the current path based on the level
        if level > current_level:
            # Move deeper: create a directory named after the previous file (without .md)
            parent_filename = hierarchy[hierarchy.index((indentation, filename, title, position)) - 1][1]
            parent_dir_name = os.path.splitext(parent_filename)[0]
            current_path = os.path.join(current_path, parent_dir_name)
            os.makedirs(current_path, exist_ok=True)

            # Create _category_.json for the parent directory
            parent_title = hierarchy[hierarchy.index((indentation, filename, title, position)) - 1][2]
            parent_position = hierarchy[hierarchy.index((indentation, filename, title, position)) - 1][3]
            create_category_json(current_path, parent_title, parent_position)
        elif level < current_level:
            # Move up: adjust the current path accordingly
            for _ in range(current_level - level):
                current_path = os.path.dirname(current_path)

        current_level = level

        # Find the source file
        source_file = find_source_file(filename, search_dir)
        if not source_file:
            print(f"Warning: File '{filename}' not found in source directory. Skipping.")
            continue

        # Determine the destination path
        if filename in has_children:
            # If the file has children, create a directory named after it (without .md)
            dir_name = os.path.splitext(filename)[0]
            new_dir = os.path.join(current_path, dir_name)
            os.makedirs(new_dir, exist_ok=True)
            destination_path = os.path.join(new_dir, filename)

            # Create _category_.json for the new directory
            create_category_json(new_dir, title, position)
        else:
            # If the file has no children, place it directly in the current directory
            destination_path = os.path.join(current_path, filename)

        # Read the original file content
        with open(source_file, 'r', encoding='utf-8') as file:
            original_content = file.read()

        # Process include statements
        updated_content = process_include_statements(original_content, search_dir)

        # Update image paths in the markdown content
        updated_content = update_image_paths(updated_content)

        # Generate the frontmatter
        frontmatter = generate_frontmatter(title, position)

        # Write the updated content to the destination path
        with open(destination_path, 'w', encoding='utf-8') as file:
            file.write(frontmatter + updated_content)

        print(f"Updated and copied: {source_file} -> {destination_path}")

        # Handle images in the markdown file
        image_paths = extract_image_paths(updated_content)
        if image_paths:
            copy_images_to_destination(destination_path, image_paths, output_dir, search_dir)

def print_directory_tree(directory, prefix=""):
    """
    Print the directory tree structure.
    """
    contents = os.listdir(directory)
    for i, item in enumerate(contents):
        path = os.path.join(directory, item)
        if os.path.isdir(path):
            print(f"{prefix}├── {item}/")
            print_directory_tree(path, prefix + "│   ")
        else:
            print(f"{prefix}├── {item}")

def reorganize_directory(output_dir, userinput):
    """
    Reorganize the directory structure by moving all files and directories
    from the parent of output_dir into the output_dir, except for the output_dir itself.
    """
    # Get the parent directory of output_dir
    parent_dir = os.path.dirname(output_dir)

    # Ensure the output_dir exists
    os.makedirs(output_dir, exist_ok=True)

    # List all items in the parent directory
    items = os.listdir(parent_dir)

    # Move each item into the output_dir
    for item in items:
        item_path = os.path.join(parent_dir, item)
        target_path = os.path.join(output_dir, item)

        # Skip the output_dir itself to avoid recursion
        if item_path == output_dir:
            continue

        # Move the item
        shutil.move(item_path, target_path)
        print(f"Moved: {item_path} -> {target_path}")

def main():
    # Check if the user provided a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <userinput>")
        sys.exit(1)

    # Get the user input from the command-line argument
    userinput = sys.argv[1]

    # Define paths
    summary_path = f"../books/{userinput}/SUMMARY.md"  # Path to SUMMARY.md
    search_dir = "."  # Current directory (collections/)
    output_dir = f"docu_book/{userinput}"  # Output directory (inside collections/)

    # Parse the SUMMARY.md file
    hierarchy = parse_summary(summary_path)

    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)

    # Print initial directory tree
    print("Initial Directory Tree:")
    print_directory_tree(output_dir)

    # Create the directory structure, copy files, add frontmatter, and create _category_.json files
    create_directory_structure(hierarchy, search_dir, output_dir)

    # Verify that all images referenced in markdown files exist in the ./img directory
    verify_images_in_markdown(output_dir, search_dir)

    # Reorganize the directory structure
    reorganize_directory(output_dir, userinput)

    # Print final directory tree
    print("\nFinal Directory Tree:")
    print_directory_tree(output_dir)

if __name__ == "__main__":
    main()