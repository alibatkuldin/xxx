import os
import jinja2

def generate_html_report(template_file='report_template.html', image_folder='report/report_images', output_file='report/report.html'):
    """
    Scans the 'image_folder' for PNG images and generates an HTML report using the specified
    Jinja2 template. The rendered report is saved as 'output_file'.
    """
    # Retrieve all PNG files from the image folder and sort them.

    image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith('.png')])

    # Build a list of dictionaries with a title (derived from the file name) and file path.
    images = []
    for filename in image_files:
        title = filename.split('.')[0].replace('_', ' ').title()
        filepath = './report_images/' + filename
        images.append({
            'title': title,
            'filepath': filepath
        })

    # Set up the Jinja2 environment with the directory containing the template file.
    template_dir = 'templates'
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template(os.path.basename(template_file))
    
    # Render the HTML template with the images list.
    rendered_html = template.render(images=images)
    
    # Write the rendered HTML to the output file.
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    
    print(f"HTML report generated: {output_file}")