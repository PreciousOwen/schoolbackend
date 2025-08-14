<?php
$content = '
<div style="max-width: 600px; margin: 50px auto; padding: 30px; background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <h2 style="text-align: center; color: #1976d2; margin-bottom: 30px;">Choose Your Role</h2>
    
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
        <div style="text-align: center; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 10px; width: 40%;">
            <h3 style="color: #1976d2;">Admin</h3>
            <p>Manage the entire system, including students, parents, drivers, buses, and routes.</p>
            <a href="/admin/dashboard.php" class="btn btn-primary" style="display: inline-block; margin-top: 10px;">Admin Dashboard</a>
        </div>
        
        <div style="text-align: center; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 10px; width: 40%;">
            <h3 style="color: #1976d2;">Parent</h3>
            <p>View your children\'s information and bus tracking details.</p>
            <a href="/parent/dashboard.php" class="btn btn-primary" style="display: inline-block; margin-top: 10px;">Parent Dashboard</a>
        </div>
        
        <div style="text-align: center; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 10px; width: 40%;">
            <h3 style="color: #1976d2;">Driver</h3>
            <p>View route information and update bus location.</p>
            <a href="/driver/dashboard.php" class="btn btn-primary" style="display: inline-block; margin-top: 10px;">Driver Dashboard</a>
        </div>
    </div>
</div>
';

include TEMPLATES_PATH . '/base.php';