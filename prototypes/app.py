from flask import Flask, render_template, request
import webview
import webview.event

app = Flask(__name__, static_folder="./static", template_folder="./templates")


@app.route("/")
def home_page():
    data = {
        "Disk A": ["Item 1.1", "Item 1.2", "Item 1.3"],
        "Disk B": ["Item 2.1", "Item 2.2"],
        "Disk C": ["Item 3.1", "Item 3.2", "Item 3.3", "Item 3.4"],
        "Disk D": ["Item 5.1", "Item 5.2", "Item 5.3", "Item 5.4", "Item 5.5"]
    }
    
    pie_data = ["1000", "980", "453", "1000", "980", "453"]
    pie_labels = [".py", ".pyc", ".txt", ".png", ".jpg"]
    
    pie_total_space = "100.0 GB"
    
    return render_template("current_disk_page.html", data=data, pie_data=pie_data, pie_labels=pie_labels, pie_total_space=pie_total_space)


@app.route("/exit")
def exit():
    if hasattr(window, "destroy"):
        window.destroy()
    
    return ''

window = webview.create_window(
    "Flask app",
    app,
    frameless=True,
    easy_drag=False,
    width=1200,
    height=800,
)

if __name__ == "__main__":
    webview.start(debug=True)
