const forms = {
  email: {title:"Email Fraud Detection", subtitle:"Check an email for common phishing warning signs.", html:`<form id="emailForm"><label class="form-label">Email subject</label><input class="form-control mb-3" name="subject" maxlength="300" placeholder="e.g. Urgent account verification"><label class="form-label">Sender email address</label><input class="form-control mb-3" name="sender" maxlength="320" placeholder="sender@example.com"><label class="form-label">Email message</label><textarea class="form-control" name="message" rows="5" maxlength="12000" placeholder="Paste the email text here. Remove private information first."></textarea><div class="form-help">Do not paste passwords, OTPs, or confidential information.</div><div class="form-actions"><button class="btn btn-neon">Analyze Email</button></div></form>`, endpoint:"/api/email"},
  url: {title:"Link / URL Detection", subtitle:"Inspect URL structure without visiting the website.", html:`<form id="urlForm"><label class="form-label">Website URL</label><input class="form-control" name="url" maxlength="2048" required placeholder="https://example.com/login"><div class="form-help">The tool will not open the URL or check a live reputation database.</div><div class="form-actions"><button class="btn btn-neon">Analyze URL</button></div></form>`, endpoint:"/api/url"},
  image: {title:"Image Fraud Screening", subtitle:"Inspect image readability and available metadata.", html:`<form id="imageForm" enctype="multipart/form-data"><label class="form-label">Choose image (JPG, JPEG, PNG)</label><input class="form-control" type="file" name="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" required><div class="form-help">Maximum file size: 8 MB. The image is processed in memory and not saved.</div><div class="form-actions"><button class="btn btn-neon">Inspect Image</button></div></form>`, endpoint:"/api/image"},
  price: {title:"Shopping Price Detection", subtitle:"Compare the listed price with a reference price you trust.", html:`<form id="priceForm"><label class="form-label">Product name (optional)</label><input class="form-control mb-3" name="name" maxlength="200" placeholder="e.g. Wireless headphones"><div class="row"><div class="col-md-6 mb-3"><label class="form-label">Displayed price (₹)</label><input class="form-control" type="number" name="displayed_price" min="0" step="0.01" required placeholder="999"></div><div class="col-md-6 mb-3"><label class="form-label">Reference price (₹)</label><input class="form-control" type="number" name="reference_price" min="0.01" step="0.01" required placeholder="2499"></div></div><div class="form-help">No shopping API is connected. Use a current price for the exact same product and variant.</div><div class="form-actions"><button class="btn btn-neon">Compare Prices</button></div></form>`, endpoint:"/api/price"},
  certificate: {title:"Certificate Screening", subtitle:"Review a certificate file and identify verification steps.", html:`<form id="certificateForm" enctype="multipart/form-data"><label class="form-label">Certificate file (PDF, JPG, JPEG, PNG)</label><input class="form-control mb-3" type="file" name="file" accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" required><div class="row"><div class="col-md-6 mb-3"><label class="form-label">Certificate ID (optional)</label><input class="form-control" name="certificate_id" maxlength="200" placeholder="Certificate number"></div><div class="col-md-6 mb-3"><label class="form-label">Issuing organization (optional)</label><input class="form-control" name="issuer" maxlength="200" placeholder="Organization name"></div></div><label class="form-label">Official verification URL (optional)</label><input class="form-control" name="verification_url" maxlength="2048" placeholder="https://official-issuer.example/verify"><div class="form-help">The supplied URL is not opened. Official database verification and OCR are not enabled.</div><div class="form-actions"><button class="btn btn-neon">Review Certificate</button></div></form>`, endpoint:"/api/certificate"}
};
const toolForm = document.getElementById("toolForm");
const resultBox = document.getElementById("resultBox");
let activeTool = null;

document.querySelectorAll("[data-tool]").forEach(button => button.addEventListener("click", () => {
  activeTool = button.dataset.tool;
  const config = forms[activeTool];
  document.getElementById("formTitle").textContent = config.title;
  document.getElementById("formSubtitle").textContent = config.subtitle;
  toolForm.innerHTML = config.html;
  resultBox.classList.add("d-none");
  resultBox.innerHTML = "";
  document.getElementById("detector").scrollIntoView({behavior:"smooth", block:"start"});
  toolForm.querySelector("form").addEventListener("submit", submitDetection);
}));

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
async function submitDetection(event) {
  event.preventDefault();
  const config = forms[activeTool];
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit],button:not([type])");
  const original = button.textContent;
  button.disabled = true; button.textContent = "Analyzing…";
  resultBox.classList.remove("d-none");
  resultBox.innerHTML = "<p>Analyzing your input…</p>";
  try {
    let response;
    if (activeTool === "image" || activeTool === "certificate") {
      response = await fetch(config.endpoint, {method:"POST", body:new FormData(form)});
    } else {
      const data = Object.fromEntries(new FormData(form).entries());
      response = await fetch(config.endpoint, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request could not be completed.");
    renderResult(data);
  } catch (err) {
    resultBox.innerHTML = `<p class="alert-error">${escapeHtml(err.message || "Something went wrong. Please try again.")}</p>`;
  } finally {
    button.disabled = false; button.textContent = original;
  }
}
function renderResult(data) {
  const reasons = (data.reasons || []).map(x => `<li>${escapeHtml(x)}</li>`).join("");
  const steps = (data.next_steps || []).map(x => `<li>${escapeHtml(x)}</li>`).join("");
  resultBox.innerHTML = `<span class="status">${escapeHtml(data.status || "Unable to Verify")}</span><p class="small mb-2"><strong>Signal level:</strong> ${escapeHtml(data.signal || "Limited heuristic check")}</p><h3>Analysis Summary</h3><ul>${reasons}</ul><h4>Recommended next steps</h4><ul>${steps}</ul><p class="small mt-3">${escapeHtml(data.explanation || "")}</p><p class="small mb-0"><strong>Disclaimer:</strong> Automated screening is not definitive proof of fraud or authenticity.</p>`;
}

document.getElementById("reportForm").addEventListener("submit", async event => {
  event.preventDefault();
  const out = document.getElementById("reportResult");
  out.textContent = "Validating…";
  try {
    const response = await fetch("/api/report", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({category:document.getElementById("reportCategory").value,description:document.getElementById("reportDescription").value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not validate report.");
    out.className = "small mt-3 alert-success";
    out.textContent = data.message;
  } catch (err) {
    out.className = "small mt-3 alert-error";
    out.textContent = err.message;
  }
});
