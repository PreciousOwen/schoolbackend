<?php
$content = '
<div style="max-width: 400px; margin: 100px auto; padding: 30px; background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <h2 style="text-align: center; color: #1976d2; margin-bottom: 30px;">Login</h2>
    
    <?php if (isset($error)): ?>
        <div style="background: #f8d7da; color: #721c24; padding: 12px; border-radius: 5px; margin-bottom: 20px;">
            <?php echo $error; ?>
        </div>
    <?php endif; ?>
    
    <form action="/auth/login.php" method="POST">
        <div style="margin-bottom: 20px;">
            <label for="username" style="display: block; margin-bottom: 8px; font-weight: 500;">Username</label>
            <input type="text" id="username" name="username" required style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px;">
        </div>
        
        <div style="margin-bottom: 20px;">
            <label for="password" style="display: block; margin-bottom: 8px; font-weight: 500;">Password</label>
            <input type="password" id="password" name="password" required style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px;">
        </div>
        
        <div style="margin-bottom: 20px;">
            <button type="submit" style="width: 100%; background: #1976d2; color: #fff; border: none; padding: 12px; border-radius: 5px; font-size: 16px; cursor: pointer;">Login</button>
        </div>
    </form>
    
    <div style="text-align: center; margin-top: 20px;">
        <a href="/auth/choose_role.php" style="color: #1976d2; text-decoration: none;">Choose Role</a>
    </div>
</div>
';

include TEMPLATES_PATH . '/base.php';