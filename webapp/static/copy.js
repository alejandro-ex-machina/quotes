document.addEventListener("click", async function (event) {
  const button = event.target.closest(".copy-btn");
  if (!button) return;

  const quote = button.dataset.quote || "";
  const author = button.dataset.author || "";
  const text = `«${quote}.»\n\n${author}`;

  try {
    await navigator.clipboard.writeText(text);

    const original = button.innerHTML;
    button.innerHTML = "✓";
    button.classList.remove("btn-outline-secondary");
    button.classList.add("btn-outline-success");

    setTimeout(() => {
      button.innerHTML = original;
      button.classList.remove("btn-outline-success");
      button.classList.add("btn-outline-secondary");
    }, 1000);
  } catch (err) {
    console.error("No se pudo copiar al portapapeles:", err);
    alert("No se pudo copiar la cita.");
  }
});
