function qs(sel) { return document.querySelector(sel); }
function qsa(sel) { return Array.from(document.querySelectorAll(sel)); }

function openModal(modal) {
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}
function closeModal(modal) {
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

async function refreshCategories(selectEl, selectNewId = null) {
  const res = await fetch("/api/categories");
  const cats = await res.json();

  const current = selectEl.value;
  selectEl.innerHTML = `<option value="" disabled>Choisir...</option>`;
  for (const c of cats) {
    const opt = document.createElement("option");
    opt.value = String(c.id);
    opt.textContent = c.name;
    selectEl.appendChild(opt);
  }
  if (selectNewId) selectEl.value = String(selectNewId);
  else if (current) selectEl.value = current;
}

function initCategoryModal() {
  const modal = qs("#categoryModal");
  const btnOpen = qs("#btnOpenCategoryModal");
  const btnCreate = qs("#btnCreateCategory");
  const btnAddSubcat = qs("#btnAddSubcategoryField");
  const select = qs("#category_id");
  const inputName = qs("#newCategoryName");
  const inputDesc = qs("#newCategoryDesc");
  const alertBox = qs("#categoryAlert");
  const subcatList = qs("#subcategoryList");
  
  // Tab buttons
  const tabNewCategory = qs("#tabNewCategory");
  const tabAddSubcat = qs("#tabAddSubcat");
  const modeNewCategory = qs("#modeNewCategory");
  const modeAddSubcat = qs("#modeAddSubcat");
  const existingCategorySelect = qs("#existingCategorySelect");
  const newSubcategoryNameAdd = qs("#newSubcategoryNameAdd");

  if (!modal || !btnOpen || !btnCreate || !select || !subcatList) return;

  let subcategoryCount = 0;
  let currentMode = "new"; // "new" or "add"

  // Add one subcategory field by default
  function addSubcategoryField() {
    const id = `subcat-${Date.now()}-${subcategoryCount++}`;
    const div = document.createElement("div");
    div.className = "field";
    div.style.display = "flex";
    div.style.gap = "8px";
    div.style.alignItems = "flex-end";
    div.innerHTML = `
      <input 
        type="text" 
        class="subcategory-input" 
        placeholder="Exemple: Photovoltaïque" 
        maxlength="100"
        style="flex: 1;"
      />
      <button type="button" class="btn danger small" onclick="this.parentElement.remove()" title="Supprimer ce type">×</button>
    `;
    subcatList.appendChild(div);
  }

  function switchMode(mode) {
    currentMode = mode;
    if (mode === "new") {
      modeNewCategory.style.display = "block";
      modeAddSubcat.style.display = "none";
      tabNewCategory.style.color = "#3498DB";
      tabNewCategory.style.borderBottomColor = "#3498DB";
      tabAddSubcat.style.color = "#999";
      tabAddSubcat.style.borderBottomColor = "transparent";
    } else {
      modeNewCategory.style.display = "none";
      modeAddSubcat.style.display = "block";
      tabNewCategory.style.color = "#999";
      tabNewCategory.style.borderBottomColor = "transparent";
      tabAddSubcat.style.color = "#3498DB";
      tabAddSubcat.style.borderBottomColor = "#3498DB";
    }
  }

  btnOpen.addEventListener("click", () => {
    alertBox.hidden = true;
    alertBox.textContent = "";
    inputName.value = "";
    inputDesc.value = "";
    subcatList.innerHTML = "";
    subcategoryCount = 0;
    addSubcategoryField();
    existingCategorySelect.value = "";
    newSubcategoryNameAdd.value = "";
    switchMode("new");
    openModal(modal);
    inputName.focus();
  });

  tabNewCategory.addEventListener("click", () => switchMode("new"));
  tabAddSubcat.addEventListener("click", () => switchMode("add"));

  if (btnAddSubcat) {
    btnAddSubcat.addEventListener("click", () => {
      addSubcategoryField();
    });
  }

  qsa("[data-close-modal]").forEach(el => {
    el.addEventListener("click", () => closeModal(modal));
  });

  modal.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal(modal);
  });

  btnCreate.addEventListener("click", async () => {
    alertBox.hidden = true;
    alertBox.textContent = "";

    if (currentMode === "new") {
      // Create new category
      const name = (inputName.value || "").trim();
      const description = (inputDesc.value || "").trim();
      const subcategoryInputs = qsa(".subcategory-input");
      const subcategories = [];

      if (!name) {
        alertBox.hidden = false;
        alertBox.textContent = "Le nom de la catégorie est obligatoire.";
        return;
      }

      for (const input of subcategoryInputs) {
        const subcatName = (input.value || "").trim();
        if (subcatName) {
          subcategories.push(subcatName);
        }
      }

      if (subcategories.length === 0) {
        alertBox.hidden = false;
        alertBox.textContent = "Vous devez ajouter au moins un type d'énergie.";
        return;
      }

      const res = await fetch("/api/categories", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ name, description, subcategories })
      });

      if (res.status === 409) {
        alertBox.hidden = false;
        alertBox.textContent = "Cette catégorie existe déjà.";
        return;
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alertBox.hidden = false;
        alertBox.textContent = err.detail || "Erreur lors de la création.";
        return;
      }

      const created = await res.json();
      await refreshCategories(select, created.id);
      closeModal(modal);
    } else {
      // Add subcategory to existing category
      const categoryId = existingCategorySelect.value;
      const name = (newSubcategoryNameAdd.value || "").trim();

      if (!categoryId) {
        alertBox.hidden = false;
        alertBox.textContent = "Sélectionnez une catégorie.";
        return;
      }

      if (!name) {
        alertBox.hidden = false;
        alertBox.textContent = "Le nom du type d'énergie est obligatoire.";
        return;
      }

      const res = await fetch("/api/subcategories", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ category_id: parseInt(categoryId), name })
      });

      if (res.status === 409) {
        alertBox.hidden = false;
        alertBox.textContent = "Ce type d'énergie existe déjà pour cette catégorie.";
        return;
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alertBox.hidden = false;
        alertBox.textContent = err.detail || "Erreur lors de l'ajout.";
        return;
      }

      // Refresh subcategories if the category is currently selected
      if (select.value === categoryId) {
        await loadSubcategories(categoryId);
      }
      closeModal(modal);
    }
  });
}

async function loadSubcategories(categoryId) {
  const subcategorySelect = qs("#subcategory_id");
  if (!subcategorySelect) return;

  subcategorySelect.innerHTML = `<option value="">Aucune</option>`;
  
  if (!categoryId) return;

  try {
    const res = await fetch(`/api/subcategories?category_id=${categoryId}`);
    if (!res.ok) return;
    
    const subcats = await res.json();
    for (const sc of subcats) {
      const opt = document.createElement("option");
      opt.value = String(sc.id);
      opt.textContent = sc.name;
      subcategorySelect.appendChild(opt);
    }
  } catch (e) {
    console.error("Erreur lors du chargement des sous-catégories:", e);
  }
}

function initSubcategoryHandler() {
  const categorySelect = qs("#category_id");
  if (!categorySelect) return;

  categorySelect.addEventListener("change", (e) => {
    loadSubcategories(e.target.value);
  });
}

function initDashboardChart() {
  const canvas = qs("#yearlyChart");
  if (!canvas || !window.Chart || !window.__chartData) return;

  const years = window.__chartData.years || [];
  const values = window.__chartData.values || [];

  // Si pas de data, Chart.js affiche quand même un canvas vide => ok.
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: years,
      datasets: [{
        label: "Somme (kWh)",
        data: values
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initCategoryModal();
  initSubcategoryHandler();
  initDashboardChart();
});
