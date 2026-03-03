document.getElementById("resFile").addEventListener("change", function () {
  if (this.files[0])
    document.getElementById("file-name").innerText = this.files[0].name;
});

async function uploadResults() {
  const file = document.getElementById("resFile").files[0];
  const batch = document.getElementById("res-batch").value;
  const sem = document.getElementById("res-sem").value;

  if (!file || !batch) {
    alert("Please select a file and enter the batch.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const token = localStorage.getItem("token");

    const res = await fetch(
      `http://127.0.0.1:8000/admin/external-marks/upload/${batch}/${sem}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      },
    );

    const data = await res.json();
    if (res.ok) alert(data.message);
    else alert("Error: " + data.detail);
  } catch (e) {
    alert("Network Error");
  }
}
