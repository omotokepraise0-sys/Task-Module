        // Initialize Bootstrap Modal
        const forgotModal = new bootstrap.Modal(document.getElementById('forgotModal'));
        
        // Toggle Password Visibility
        const togglePassword = document.getElementById('togglePassword');
        const password = document.getElementById('password');
        
        togglePassword.addEventListener('click', function() {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
        
        // Forgot Password Link
        document.getElementById('forgotPassword').addEventListener('click', function(e) {
            e.preventDefault();
            forgotModal.show();
        });
        
        // Send Reset Email
        document.getElementById('sendResetBtn').addEventListener('click', function() {
            const email = document.getElementById('resetEmail').value;
            if (email) {
                alert(`Password reset instructions sent to ${email}`);
                forgotModal.hide();
                document.getElementById('resetEmail').value = '';
            } else {
                alert('Please enter your email address');
            }
        });
        
        // Form Submission
        const loginForm = document.getElementById('loginForm');
        const loginBtn = document.getElementById('loginBtn');
        const btnText = loginBtn.querySelector('.btn-text');
        const btnLoader = loginBtn.querySelector('.btn-loader');
        const successMessage = document.getElementById('successMessage');
        
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get values
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            
            // Reset errors
            document.querySelectorAll('.form-control').forEach(el => {
                el.classList.remove('is-invalid');
            });
            document.querySelectorAll('.error-message').forEach(el => {
                el.textContent = '';
            });
            
            let isValid = true;
            
            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                document.getElementById('email').classList.add('is-invalid');
                document.getElementById('emailError').textContent = 'Please enter a valid email address';
                isValid = false;
            }
            
            // Validate password
            if (password.length < 6) {
                document.getElementById('password').classList.add('is-invalid');
                document.getElementById('passwordError').textContent = 'Password must be at least 6 characters';
                isValid = false;
            }
            
            if (isValid) {
                // Show loading state
                btnText.style.display = 'none';
                btnLoader.style.display = 'inline-block';
                loginBtn.classList.add('loading');
                
                // Simulate API call
                setTimeout(() => {
                    // Check demo credentials
                    if (email === 'demo@taskflow.com' && password === 'password123') {
                        // Success!
                        successMessage.style.display = 'flex';
                        btnLoader.style.display = 'none';
                        btnText.style.display = 'inline';
                        loginBtn.classList.remove('loading');
                        
                        // Change button to success state
                        loginBtn.innerHTML = '<i class="fas fa-check-circle"></i> Login Successful!';
                        loginBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
                        
                        // Redirect to dashboard after 2 seconds
                        setTimeout(() => {
                            alert('Redirecting to dashboard... (Demo)');
                            // In real app: window.location.href = 'dashboard.html';
                            
                            // Reset form
                            loginBtn.innerHTML = 'Sign In';
                            loginBtn.style.background = 'linear-gradient(135deg, var(--accent-color) 0%, #2563eb 100%)';
                            successMessage.style.display = 'none';
                        }, 2000);
                    } else {
                        // Invalid credentials
                        btnLoader.style.display = 'none';
                        btnText.style.display = 'inline';
                        loginBtn.classList.remove('loading');
                        
                        document.getElementById('password').classList.add('is-invalid');
                        document.getElementById('passwordError').textContent = 'Invalid email or password';
                        
                        // Show demo hint
                        alert('Demo credentials: demo@taskflow.com / password123');
                    }
                }, 1500);
            }
        });
        
        // Social Login Handlers
        document.getElementById('googleLogin').addEventListener('click', function() {
            alert('Google login would open here (Demo)');
        });
        
        document.getElementById('facebookLogin').addEventListener('click', function() {
            alert('Facebook login would open here (Demo)');
        });
        
        // Quick fill demo credentials
        document.querySelector('.demo-notice').addEventListener('click', function() {
            document.getElementById('email').value = 'demo@taskflow.com';
            document.getElementById('password').value = 'password123';
            
            // Highlight fields briefly
            document.getElementById('email').style.backgroundColor = '#f0f9ff';
            document.getElementById('password').style.backgroundColor = '#f0f9ff';
            
            setTimeout(() => {
                document.getElementById('email').style.backgroundColor = '';
                document.getElementById('password').style.backgroundColor = '';
            }, 500);
        });
        
        // Enter key press handler
        password.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loginForm.dispatchEvent(new Event('submit'));
            }
        });