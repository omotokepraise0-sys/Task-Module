        // Toggle mobile menu
        const header = document.querySelector('.header .page-title');
        if (header) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'btn btn-light me-3';
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            toggleBtn.style.display = 'none';
            toggleBtn.onclick = () => {
                const sidebar = document.querySelector('.sidebar');
                if (sidebar) sidebar.classList.toggle('active');
            };
            
            if (window.innerWidth <= 768) {
                toggleBtn.style.display = 'inline-block';
            }
            header.prepend(toggleBtn);

            window.addEventListener('resize', function() {
                if (window.innerWidth <= 768) {
                    toggleBtn.style.display = 'inline-block';
                } else {
                    toggleBtn.style.display = 'none';
                    const sidebar = document.querySelector('.sidebar');
                    if (sidebar) sidebar.classList.remove('active');
                }
            });
        }
        
        // Removed toggleBtn reference - safe null check version
        window.addEventListener('resize', function() {
            const toggleBtn = document.querySelector('.menu-toggle');
            if (window.innerWidth <= 768) {
                if (toggleBtn) toggleBtn.style.display = 'inline-block';
            } else {
                if (toggleBtn) toggleBtn.style.display = 'none';
                const sidebar = document.querySelector('.sidebar');
                if (sidebar) sidebar.classList.remove('active');
            }
        });

        
        // View toggle
        const listView = document.getElementById('listView');
        const gridView = document.getElementById('gridView');
        const viewBtns = document.querySelectorAll('.view-btn');
        
        viewBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                viewBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                if (this.dataset.view === 'list') {
                    listView.style.display = 'block';
                    gridView.classList.remove('active');
                } else {
                    listView.style.display = 'none';
                    gridView.classList.add('active');
                }
            });
        });
        
        // Filter tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                filterTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // In real app, this would filter tasks
                alert(`Filtering by: ${this.dataset.filter}`);
            });
        });
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function() {
            if (this.value.length > 2) {
                // In real app, this would search tasks
                console.log(`Searching for: ${this.value}`);
            }
        });
        
        // Bulk actions
        const taskSelectors = document.querySelectorAll('.task-select');
        const bulkActions = document.getElementById('bulkActions');
        const selectedCount = document.getElementById('selectedCount');
        
        taskSelectors.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedCount = document.querySelectorAll('.task-select:checked').length;
                selectedCount.textContent = checkedCount;
                
                if (checkedCount > 0) {
                    bulkActions.classList.add('active');
                } else {
                    bulkActions.classList.remove('active');
                }
            });
        });
        
        // Bulk action buttons
        document.getElementById('bulkComplete').addEventListener('click', function() {
            alert('Marking selected tasks as complete');
        });
        
        document.getElementById('bulkPriority').addEventListener('click', function() {
            alert('Opening priority selector for selected tasks');
        });
        
        document.getElementById('bulkDelete').addEventListener('click', function() {
            if (confirm('Are you sure you want to delete selected tasks?')) {
                alert('Deleting selected tasks');
            }
        });
        
        document.getElementById('bulkCancel').addEventListener('click', function() {
            taskSelectors.forEach(checkbox => {
                checkbox.checked = false;
            });
            bulkActions.classList.remove('active');
        });
        
        // FAB click
        document.querySelector('.fab').addEventListener('click', function() {
            alert('Create new task form would open here!');
        });
        
        // Task action buttons
        document.querySelectorAll('.task-action-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                if (this.classList.contains('delete')) {
                    if (confirm('Delete this task?')) {
                        this.closest('.task-item').remove();
                    }
                } else if (this.querySelector('.fa-edit')) {
                    alert('Edit task form would open here');
                } else if (this.querySelector('.fa-copy')) {
                    alert('Task duplicated!');
                }
            });
        });
        
        // Task card buttons
        document.querySelectorAll('.task-card-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                if (this.classList.contains('delete')) {
                    if (confirm('Delete this task?')) {
                        this.closest('.task-card').remove();
                    }
                } else if (this.textContent.includes('Edit')) {
                    alert('Edit task form would open here');
                } else if (this.textContent.includes('Complete')) {
                    alert('Task marked as complete');
                } else if (this.textContent.includes('Reopen')) {
                    alert('Task reopened');
                }
            });
        });
        
        // Notification badge
        document.querySelector('.notification-badge').addEventListener('click', function() {
            alert('You have 3 notifications');
        });