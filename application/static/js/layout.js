const desktop = document.querySelector('main');
const minSize = 250;

const domCache = new Map();
const tabs = document.querySelectorAll('section .tabs li');
const tabLoaders = {
   "documents/templates": () => import("./documents/templates.js"),
   "viewer/map": () => import("./viewer/map.js"),
   "viewer/editor": () => import("./viewer/editor.js")
};



// Rezisable layout

const columns = {
   left: document.querySelector('.main-grid.grid-1'),
   right: document.querySelector('.main-grid.grid-2')
};

function startResize(event) {
   event.preventDefault();
   const handle = event.target;
   const axis = handle.dataset.axis;

   function move(e) {
      if (axis === 'x') {
         const rect = desktop.getBoundingClientRect();
         let x = e.clientX - rect.left;
         x = Math.max(minSize, Math.min(rect.width - minSize, x));
         desktop.style.setProperty('--left', `${x}px`);
      } else {
         const colName = handle.dataset.column;
         const col = columns[colName];
         const rect = col.getBoundingClientRect();
         let y = e.clientY - rect.top;
         y = Math.max(minSize, Math.min(rect.height - minSize, y));
         desktop.style.setProperty(`--top-${colName}`, `${y}px`);
      }
   }

   function stop() {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', stop);
   }

   window.addEventListener('pointermove', move);
   window.addEventListener('pointerup', stop);
}

document.querySelectorAll('.handle').forEach(handle =>
   handle.addEventListener('pointerdown', startResize)
);

// Tabs loading

async function loadTab(key, view) {
   // Load tab content via AJAX
   const response = await fetch(`ajax/tabs/${key}`);
   if (!response.ok) throw new Error(`Failed to load tab /${key}`);
   const html = await response.text();
   view.innerHTML = html;
   // Load tab module
   const loader = tabLoaders[key];
   if (!loader) return null;
   const module = await loader();
   return module;
}

async function switchTab(tab) {
   const section = tab.closest('section');
   const view = section.querySelector('.view');
   const sectionId = section.dataset.sectionId;
   const tabId = tab.dataset.tabId;
   const prevTabId = view.dataset.activeView;

   const key = `${sectionId}/${tabId}`;
   const cache = domCache.get(key);

   if (tabId === prevTabId) {
      // No change
      return cache.module
   }

   // Deselect all tabs
   section.querySelectorAll('.tabs li').forEach(t => t.classList.remove('selected'));
   // Select clicked tab
   tab.classList.add('selected');

   if (cache) {
      // Loads tab from cache if exists
      view.replaceChildren(cache.node);
   } else {
      // Otherwise load tab content and save in cache
      try {
         const module = await loadTab(key, view);
         domCache.set(key, { node: view.firstElementChild, module });
      } catch (err) {
         view.innerHTML = "<p class='error'>Error loading content.</p>";
         view.dataset.activeView = "";
         console.error(err);
         return
      }
   }

   view.dataset.activeView = tabId;
   return domCache.get(key).module
}


// Switch tab on click
tabs.forEach(tab => {
   tab.addEventListener('click', () => switchTab(tab));
});


// Load default tabs
document.querySelectorAll('section').forEach(section => {
   const defaultTab = section.querySelector('.tabs li.selected');
   if (defaultTab) {
      switchTab(defaultTab);
   }
});