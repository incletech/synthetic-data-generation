import chainlit as cl

@cl.app
def main():
    # Title Section
    cl.Title("LLAMA X")
    cl.Subtitle("THE KILLER")
    cl.Text("UPLOAD YOUR FILES IN CSV TO GET STARTED")

    # Model Selection Dropdown
    model_dropdown = cl.Dropdown(
        label="Model",
        options=[
            cl.Option("Model A", value="model_a"),
            cl.Option("Model B", value="model_b"),
            cl.Option("Model C", value="model_c")
        ],
        placeholder="Select Model"
    )

    # Output Format Selection Dropdown
    output_format_dropdown = cl.Dropdown(
        label="Output Format",
        options=[
            cl.Option("CSV", value="csv"),
            cl.Option("JSON", value="json"),
            cl.Option("XML", value="xml")
        ],
        placeholder="Select Output Format"
    )

    # Sample Data Download Button
    sample_data_button = cl.Button(
        label="Download",
        color="green",
        action=download_sample_data
    )

    # File Upload Section
    file_input = cl.FileInput(
        label="Choose File",
        accept=".csv"
    )

    upload_button = cl.Button(
        label="Upload",
        color="blue",
        action=upload_file
    )

    # Previously Generated Files Dropdown
    previously_generated_files_dropdown = cl.Dropdown(
        label="Previously Generated Files",
        options=[
            cl.Option("File 1", value="file_1"),
            cl.Option("File 2", value="file_2"),
            cl.Option("File 3", value="file_3")
        ],
        placeholder="Select a file"
    )

    # Layout
    layout = cl.Layout([
        [model_dropdown, output_format_dropdown, sample_data_button],
        [file_input, upload_button],
        [previously_generated_files_dropdown]
    ])

    # Render the layout
    layout.render()

# Action Functions
def download_sample_data():
    # Logic to download sample data
    cl.Text("Downloading sample data...").render()

def upload_file(file):
    # Logic to handle file upload
    cl.Text(f"Uploading file: {file.filename}").render()
