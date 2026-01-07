// Custom JavaScript for TANI'S BOOK STORE

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Form validation enhancement
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Phone number validation
const phoneInputs = document.querySelectorAll('input[type="tel"]');
phoneInputs.forEach(function(input) {
    input.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
});

// Confirm before important actions (subtract operations)
document.addEventListener('DOMContentLoaded', function() {
    // Add confirmation to subtract stock actions
    const updateModal = document.getElementById('updateModal');
    if (updateModal) {
        updateModal.addEventListener('submit', function(e) {
            const action = document.getElementById('modal_action').value;
            const quantity = document.getElementById('modal_quantity').value;
            const bookName = document.getElementById('modal_book_name').value;
            
            if (action === 'subtract') {
                if (!confirm(`Are you sure you want to subtract ${quantity} units from "${bookName}"?`)) {
                    e.preventDefault();
                }
            }
        });
    }
});

// Dynamic book selection in sell form with auto-fill
document.addEventListener('DOMContentLoaded', function() {
    const bookIdInput = document.getElementById('book_id');
    if (bookIdInput) {
        // Store book data from page using data attributes or table structure
        const bookData = {};
        const bookRows = document.querySelectorAll('tr[style*="cursor: pointer"]');
        bookRows.forEach(function(row) {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 4) {
                const bookId = cells[0].textContent.trim();
                bookData[bookId] = {
                    name: cells[1].textContent.trim(),
                    stock: parseInt(cells[2].querySelector('.badge')?.textContent.trim() || '0'),
                    price: cells[3].textContent.trim()
                };
            }
        });
        
        // Show stock availability when book ID changes
        bookIdInput.addEventListener('change', function() {
            const bookId = this.value.trim();
            if (bookData[bookId]) {
                const book = bookData[bookId];
                showStockInfo(book.name, book.stock, book.price);
            }
        });
        
        bookIdInput.addEventListener('blur', function() {
            const bookId = this.value.trim();
            if (bookData[bookId]) {
                const book = bookData[bookId];
                showStockInfo(book.name, book.stock, book.price);
            }
        });
    }
});

// Show stock availability information
function showStockInfo(bookName, stock, price) {
    // Remove existing stock info
    const existingInfo = document.querySelector('.stock-availability-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    // Create and display stock info
    const bookIdInput = document.getElementById('book_id');
    if (bookIdInput) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'alert alert-info alert-dismissible fade show mt-2 stock-availability-info';
        infoDiv.innerHTML = `
            <strong>${bookName}</strong><br>
            Available Stock: <span class="badge ${stock < 10 ? 'bg-warning' : 'bg-success'}">${stock}</span>
            Price: ${price}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        bookIdInput.parentElement.appendChild(infoDiv);
    }
}

// Table search/filter functionality
let tableSearchCounter = 0;

document.addEventListener('DOMContentLoaded', function() {
    // Add search box to tables if they have more than 5 rows
    const tables = document.querySelectorAll('table.table');
    tables.forEach(function(table) {
        const tbody = table.querySelector('tbody');
        if (tbody && tbody.querySelectorAll('tr').length > 5) {
            addSearchToTable(table);
        }
    });
});

function addSearchToTable(table) {
    // Check if search already exists
    if (table.previousElementSibling && table.previousElementSibling.classList.contains('table-search-box')) {
        return;
    }
    
    // Create unique ID using counter
    const searchId = 'tableSearch_' + (++tableSearchCounter);
    
    // Create search input
    const searchContainer = document.createElement('div');
    searchContainer.className = 'mb-3 table-search-box';
    searchContainer.innerHTML = `
        <div class="input-group">
            <span class="input-group-text"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control" placeholder="Search table..." id="${searchId}">
        </div>
    `;
    
    // Insert before table
    table.parentElement.insertBefore(searchContainer, table);
    
    // Add search functionality
    const searchInput = searchContainer.querySelector('input');
    searchInput.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        rows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Confirm before important actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

// Add loading state to buttons
function addLoadingState(button) {
    button.disabled = true;
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    return function() {
        button.disabled = false;
        button.innerHTML = originalText;
    };
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Real-time quantity validation in sell form
document.addEventListener('DOMContentLoaded', function() {
    const quantityInput = document.getElementById('quantity');
    const bookIdInput = document.getElementById('book_id');
    
    if (quantityInput && bookIdInput) {
        quantityInput.addEventListener('input', function() {
            validateQuantity();
        });
        
        bookIdInput.addEventListener('change', function() {
            validateQuantity();
        });
    }
});

function validateQuantity() {
    const quantityInput = document.getElementById('quantity');
    const bookIdInput = document.getElementById('book_id');
    
    if (!quantityInput || !bookIdInput) return;
    
    const quantity = parseInt(quantityInput.value);
    const bookId = bookIdInput.value.trim();
    
    // Get stock from the table using table structure instead of onclick attribute
    const bookRows = document.querySelectorAll('tr[style*="cursor: pointer"]');
    let availableStock = null;
    
    bookRows.forEach(function(row) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3) {
            const rowBookId = cells[0].textContent.trim();
            if (rowBookId === bookId) {
                const stockBadge = cells[2].querySelector('.badge');
                if (stockBadge) {
                    availableStock = parseInt(stockBadge.textContent.trim());
                }
            }
        }
    });
    
    // Remove existing validation message
    const existingMsg = quantityInput.parentElement.querySelector('.quantity-validation-msg');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Validate and show message
    if (availableStock !== null && quantity > availableStock) {
        quantityInput.classList.add('is-invalid');
        const msgDiv = document.createElement('div');
        msgDiv.className = 'invalid-feedback quantity-validation-msg';
        msgDiv.textContent = `Only ${availableStock} units available in stock`;
        quantityInput.parentElement.appendChild(msgDiv);
    } else {
        quantityInput.classList.remove('is-invalid');
    }
}

// Console log for debugging (remove in production)
console.log('TANI\'S BOOK STORE - Application loaded successfully');
