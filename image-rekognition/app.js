const API =
  "https://sunzqiq8p6.execute-api.us-east-1.amazonaws.com/prod";

// Load categories from DB
async function loadCategories() {
  const res = await fetch(`${API}/categories`);
  const categories = await res.json();

  const container = document.getElementById("categories");
  container.innerHTML = "";

  categories.forEach(category => {
    const btn = document.createElement("button");
    btn.innerText = category;
    btn.onclick = () => loadImages(category);
    container.appendChild(btn);
  });
}

// Load images of selected category
async function loadImages(category) {
  const res = await fetch(
    `${API}/images?category=${category}`
  );

  const images = await res.json();
  const container = document.getElementById("images");
  container.innerHTML = "";

  if (images.length === 0) {
    container.innerText = "No images found";
    return;
  }

  images.forEach(url => {
    const img = document.createElement("img");
    img.src = url;
    img.width = 200;
    img.style.margin = "10px";
    container.appendChild(img);
  });
}

// Start app
loadCategories();
