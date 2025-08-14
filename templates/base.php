<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?></title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,500,700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #1976d2;
            --primary-dark: #125ea2;
            --danger: #d32f2f;
            --background: #f4f6f8;
            --card-bg: #fff;
            --border: #e0e0e0;
            --radius: 10px;
        }
        body {
            background: var(--background);
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .navbar {
            background: var(--primary);
            color: #fff;
            padding: 18px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .navbar a {
            color: #fff;
            text-decoration: none;
            font-weight: 500;
            margin-left: 24px;
            transition: color 0.2s;
        }
        .navbar a:hover {
            color: #e3e3e3;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .logout-link {
            color: #fff;
            font-weight: 500;
            margin-left: 20px;
        }
        .logout-link:hover {
            color: #ffc107;
        }
        hr {
            border: 0;
            border-top: 1px solid var(--border);
            margin: 0;
        }
        .btn {
            display: inline-block;
            padding: 8px 18px;
            border-radius: 6px;
            font-weight: 500;
            text-decoration: none;
            transition: background 0.2s;
            border: none;
            cursor: pointer;
        }
        .btn-primary {
            background: var(--primary);
            color: #fff;
        }
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        .btn-secondary {
            background: #fff;
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        .btn-secondary:hover {
            background: var(--primary);
            color: #fff;
        }
        .btn-danger {
            background: var(--danger);
            color: #fff;
        }
        .btn-danger:hover {
            background: #b21010;
        }
        .text-muted {
            color: #888;
        }
        .alert {
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div style="font-size: 1.5em; font-weight: 700; letter-spacing: 1px;"><?php echo APP_NAME; ?></div>
        <div>
            <?php if (isLoggedIn()): ?>
                <span>Welcome, <?php echo $_SESSION['user_name'] ?? 'User'; ?></span>
                <a href="/auth/logout.php" class="logout-link">Logout</a>
            <?php else: ?>
                <a href="/auth/login.php">Login</a>
                <a href="/auth/choose_role.php">Choose Role</a>
            <?php endif; ?>
        </div>
    </div>
    <hr>
    <div class="container">
        <?php if (isset($_SESSION['success_message'])): ?>
            <div class="alert alert-success"><?php echo $_SESSION['success_message']; ?></div>
            <?php unset($_SESSION['success_message']); ?>
        <?php endif; ?>
        
        <?php if (isset($_SESSION['error_message'])): ?>
            <div class="alert alert-error"><?php echo $_SESSION['error_message']; ?></div>
            <?php unset($_SESSION['error_message']); ?>
        <?php endif; ?>
        
        <?php echo $content ?? ''; ?>
    </div>
</body>
</html>