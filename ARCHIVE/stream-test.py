import webbrowser
import time

# Base HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Page</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }}
        .header {{
            background-color: #333;
            color: white;
            text-align: center;
            padding: 10px 0;
            font-size: 24px;
        }}
        .container {{
            width: 100%;
            height: calc(100% - 50px);
            position: relative;
        }}
        #streamIframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <div class="header">Live Stream</div>
    <div class="container">
        <iframe id="streamIframe" src="https://olalivehdplay.ru/premiumtv/poscitechs.php?id={id}" allow="encrypted-media" allowfullscreen="true" allowtransparency="true"></iframe>
    </div>

    <script>
        document.getElementById('streamIframe').onload = function() {{
            const iframe = document.getElementById('streamIframe');
            const iframeWindow = iframe.contentWindow;
            const iframeDocument = iframeWindow.document;

            // Function to remove all iframes and unwanted elements except the main one
            const removeUnwantedElements = () => {{
                const adsSelectors = [
                    'iframe', // Remove all iframes
                    'script[src*="ads"]', // Ad scripts
                    'div[style*="position: absolute"]', // Overlay ads
                    '.overlay', // Common class name for overlay ads
                ];

                adsSelectors.forEach(selector => {{
                    const elements = iframeDocument.querySelectorAll(selector);
                    elements.forEach(element => {{
                        if (element !== iframe) {{
                            console.log('Removing:', element);
                            element.remove();
                        }}
                    }});
                }});
            }};

            // Prevent clicks from opening new tabs or ads
            const preventClicks = (event) => {{
                event.stopPropagation();
                event.preventDefault();
                console.log('Blocked a click event:', event);
            }};

            // Add event listener to capture and prevent click events
            iframeDocument.addEventListener('click', preventClicks, true);
            iframeDocument.addEventListener('contextmenu', preventClicks, true); // Prevent right-click events

            // Initially remove unwanted elements
            removeUnwantedElements();

            // Continuously remove unwanted elements and prevent clicks at intervals
            setInterval(() => {{
                removeUnwantedElements();
                iframeDocument.addEventListener('click', preventClicks, true);
                iframeDocument.addEventListener('contextmenu', preventClicks, true); // Prevent right-click events
            }}, 1000);

            // Overriding methods to prevent the creation of new iframes
            const originalCreateElement = iframeDocument.createElement.bind(iframeDocument);
            iframeDocument.createElement = function(tagName) {{
                if (tagName.toLowerCase() === 'iframe') {{
                    console.log('Blocked an attempt to create an iframe');
                    return originalCreateElement('div'); // Return a harmless element instead
                }}
                return originalCreateElement(tagName);
            }};

            const originalAppendChild = iframeDocument.body.appendChild.bind(iframeDocument.body);
            iframeDocument.body.appendChild = function(element) {{
                if (element.tagName && element.tagName.toLowerCase() === 'iframe') {{
                    console.log('Blocked an attempt to append an iframe');
                    return element; // Block the iframe
                }}
                return originalAppendChild(element);
            }};
        }};
    </script>
</body>
</html>
"""

# Function to generate HTML with a specific ID and open it in a browser tab
def open_html_with_id(id):
    html_content = html_template.format(id=id)
    file_name = f'stream_{id}.html'
    with open(file_name, 'w') as file:
        file.write(html_content)
    webbrowser.open(f'file://{file_name}')

# Open HTML in browser tabs with IDs from 1 to 10
for i in range(1, 11):
    open_html_with_id(i)
    time.sleep(1)  # Add a slight delay to avoid overwhelming the browser
