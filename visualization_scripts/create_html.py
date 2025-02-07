html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Table Layout</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            text-align: center;
            padding: 10px;
        }
        img, video {
            max-width: 100%;
            height: auto;
            display: block;
            margin: auto;
        }
    </style>
</head>
<body>
    <table>
        <tr>
            <th>Text Input</th>
            <th>Violin</th>
            <th>Dog</th>
            <th>Gun</th>
        </tr>
        <tr>
            <td>Image Input and text</td>
            <td>
                <img src="violin.jpg" alt="Violin Image">
                A small girl is playing a violin with a bow.
            </td>
            <td>
                <img src="dog.jpg" alt="Dog Image">
                A dog is barking.
            </td>
            <td>
                <img src="gun.jpg" alt="Gun Image">
                A gunshot is being fired.
            </td>
        </tr>
        <tr>
            <td>Pyramid Flow (SD3 backbone)</td>
            <td>
                <video controls>
                    <source src="violin_sd3_orig.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="dog_sd3_orig.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="gun_sd3_orig.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
        </tr>
        <tr>
            <td>Pyramid Flow (SD3 backbone) Finetuned 40K</td>
            <td>
                <video controls>
                    <source src="violin_sd3_40k.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="dog_sd3_40k.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="gun_sd3_40k.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
        </tr>
                <tr>
            <td>Pyramid Flow (Flux backbone)</td>
            <td>
                <video controls>
                    <source src="violin_flux_orig.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="dog_flux_orig.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="gun_flux_orig.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
        </tr>
        <tr>
            <td>Pyramid Flow (Flux backbone) Finetuned 40K</td>
            <td>
                <video controls>
                    <source src="violin_flux_40k.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="dog_flux_40k.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
            <td>
                <video controls>
                    <source src="gun_flux_40k.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </td>
        </tr>



        
    </table>
</body>
</html>
"""

# Save the HTML content to a file
file_path = "/home/sxk230060/TI2AV/Pyramid-Flow/temp_samples/temp.html"
with open(file_path, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"HTML file saved as {file_path}")
