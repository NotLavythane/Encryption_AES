let state = {
  key: null,
  ciphertext: null,
  mode: "CBC"
};

document.getElementById("mode").onchange = () => invalidate();

function invalidate() {
  state.key = null;
  state.ciphertext = null;
  document.getElementById("keyStatus").innerText = "🔴 Secret Invalid";
  document.getElementById("cryptoArea").classList.add("disabled");
}

function generateKey() {
  fetch("/generate-key", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({size: document.getElementById("keySize").value})
  }).then(r=>r.json()).then(d=>{
    state.key = d.key;
    document.getElementById("keyDisplay").value = d.key;
    document.getElementById("keyStatus").innerText = "🟢 Secret Ready";
    document.getElementById("keyStatus").className = "green";
    document.getElementById("cryptoArea").classList.remove("disabled");
  });
}

function encrypt() {
  fetch("/encrypt", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      key: state.key,
      plaintext: document.getElementById("plaintext").value,
      mode: document.getElementById("mode").value
    })
  }).then(r=>r.json()).then(d=>{
    state.ciphertext = d.ciphertext;
    document.getElementById("ciphertext").value = d.ciphertext;
  });
}

function decrypt() {
  fetch("/decrypt", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      key: state.key,
      ciphertext: state.ciphertext,
      mode: document.getElementById("mode").value
    })
  }).then(r=>r.json()).then(d=>{
    document.getElementById("plaintext").value = d.plaintext;
  });
}

function bitflip() {
  fetch("/bitflip", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({ciphertext: state.ciphertext})
  }).then(r=>r.json()).then(d=>{
    state.ciphertext = d.ciphertext;
    document.getElementById("ciphertext").value = d.ciphertext;
  });
}

function exportData() {
  const blob = new Blob([state.ciphertext], {type:"text/plain"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "encrypted.txt";
  a.click();
}
