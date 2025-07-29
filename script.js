document.addEventListener("DOMContentLoaded", function () {
  const itemSelect = document.getElementById("item");
  const priceInput = document.getElementById("price");
  const addItemBtn = document.getElementById("addItem");
  const itemsList = document.getElementById("itemsList");
  const grandTotalCell = document.getElementById("grandTotal");
  const form = document.querySelector("form");

  let items = [];
  let counter = 1;

  // Update price when item is selected
  itemSelect.addEventListener("change", function () {
    if (this.value) {
      const selectedOption = this.options[this.selectedIndex];
      priceInput.value = selectedOption.dataset.price;
    } else {
      priceInput.value = "";
    }
  });

  // Add item to the list
  addItemBtn.addEventListener("click", function () {
    const itemName = itemSelect.value;
    const quantity = document.getElementById("quantity").value;
    const price = priceInput.value;

    if (!itemName || !quantity || !price) {
      alert("Mohon lengkapi semua field!");
      return;
    }

    const total = parseInt(quantity) * parseInt(price);
    const item = {
      id: Date.now(),
      name: itemName,
      quantity: quantity,
      price: price,
      total: total,
    };

    items.push(item);
    renderItems();
    calculateTotal();

    // Reset form
    itemSelect.value = "";
    document.getElementById("quantity").value = "1";
    priceInput.value = "";
    itemSelect.focus();
  });

  // Remove item from the list
  itemsList.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-item")) {
      const itemId = parseInt(e.target.dataset.id);
      items = items.filter((item) => item.id !== itemId);
      renderItems();
      calculateTotal();
    }
  });

  // Before form submission, add hidden inputs for each item
  form.addEventListener("submit", function (e) {
    // Validasi client-side
    if (items.length === 0) {
      e.preventDefault(); // Mencegah form disubmit jika tidak ada barang
      alert("Minimal harus ada 1 barang");
      return;
    }

    if (!document.getElementById("nama").value.trim()) {
      e.preventDefault(); // Mencegah form disubmit jika nama pelanggan kosong
      alert("Nama pelanggan harus diisi");
      return;
    }

    // Tambahkan hidden inputs
    items.forEach((item) => {
      const itemInput = document.createElement("input");
      itemInput.type = "hidden";
      itemInput.name = "item[]";
      itemInput.value = item.name;
      form.appendChild(itemInput);

      const quantityInput = document.createElement("input");
      quantityInput.type = "hidden";
      quantityInput.name = "quantity[]";
      quantityInput.value = item.quantity;
      form.appendChild(quantityInput);

      const priceInput = document.createElement("input");
      priceInput.type = "hidden";
      priceInput.name = "price[]";
      priceInput.value = item.price;
      form.appendChild(priceInput);
    });

    // Tidak ada e.preventDefault() yang perlu dihapus di sini
    // jika Anda ingin form disubmit secara normal ke target="_blank"
    // Validasi di atas akan menghentikan submit jika kondisi tidak terpenuhi.
  });

  // Render items in the table
  function renderItems() {
    itemsList.innerHTML = "";
    counter = 1;

    items.forEach((item) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${counter++}</td>
                <td>${item.name}</td>
                <td>${item.quantity}</td>
                <td>Rp ${parseInt(item.price).toLocaleString("id-ID")}</td>
                <td>Rp ${item.total.toLocaleString("id-ID")}</td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm remove-item" data-id="${
                      item.id
                    }">
                        Hapus
                    </button>
                </td>
            `;
      itemsList.appendChild(row);
    });
  }

  // Calculate grand total
  function calculateTotal() {
    const grandTotal = items.reduce((sum, item) => sum + item.total, 0);
    grandTotalCell.textContent = `Rp ${grandTotal.toLocaleString("id-ID")}`;
  }
});
