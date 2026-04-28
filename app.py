from flask import Flask, request, jsonify, render_template, send_file
from Simulation import run_simulation_api, generate_excel_file

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400

        result = run_simulation_api(data)

        return jsonify({
            "success": True,
            "message": "Simulation completed successfully",
            "data": result
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route("/download-excel", methods=["POST"])
def download_excel():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400

        results = data.get("results", [])
        summary = data.get("summary", {})

        if not results:
            return jsonify({
                "success": False,
                "error": "No results available to export"
            }), 400

        excel_file = generate_excel_file(results, summary)

        return send_file(
            excel_file,
            as_attachment=True,
            download_name="simulation_results.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
