<?php
$content = '
<div class="admin-dashboard">
  <h2>Admin Dashboard</h2>
  <div class="dashboard-section">
    <h3>Quick Actions</h3>
    <a href="/admin/register_all.php" class="btn btn-primary">Register Parent, Driver & Student</a>
    <a href="/admin/export_boarding_history.php" class="btn btn-secondary">Download Boarding History (CSV)</a>
  </div>
  
  <div class="dashboard-section">
    <h3>Students <a href="/admin/student_add.php" class="btn btn-primary" style="float:right;">Add Student</a></h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #e0e0e0;">
      <tr style="background: #f4f6f8;"><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Name</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">RFID</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Parent</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Route</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Actions</th></tr>
      <?php foreach ($students as $student): ?>
      <tr>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($student["name"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($student["rfid"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($student["parent_phone"] ?? ""); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($student["route_name"] ?? ""); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;">
          <a href="/admin/student_edit.php?id=<?php echo $student["id"]; ?>" class="btn btn-secondary" style="background:#ffa000; display: inline-block; margin: 2px;">Edit</a>
          <a href="/admin/student_delete.php?id=<?php echo $student["id"]; ?>" class="btn btn-danger" style="display: inline-block; margin: 2px;">Delete</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>
  </div>
  
  <div class="dashboard-section">
    <h3>Parents <a href="/admin/parent_add.php" class="btn btn-primary" style="float:right;">Add Parent</a></h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #e0e0e0;">
      <tr style="background: #f4f6f8;"><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Name</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Phone</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Actions</th></tr>
      <?php foreach ($parents as $parent): ?>
      <tr>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($parent["first_name"] . " " . $parent["last_name"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($parent["phone_number"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;">
          <a href="/admin/parent_edit.php?id=<?php echo $parent["id"]; ?>" class="btn btn-secondary" style="background:#ffa000; display: inline-block; margin: 2px;">Edit</a>
          <a href="/admin/parent_delete.php?id=<?php echo $parent["id"]; ?>" class="btn btn-danger" style="display: inline-block; margin: 2px;">Delete</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>
  </div>
  
  <div class="dashboard-section">
    <h3>Drivers <a href="/admin/driver_add.php" class="btn btn-primary" style="float:right;">Add Driver</a></h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #e0e0e0;">
      <tr style="background: #f4f6f8;"><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Name</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Phone</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Actions</th></tr>
      <?php foreach ($drivers as $driver): ?>
      <tr>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($driver["first_name"] . " " . $driver["last_name"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($driver["phone_number"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;">
          <a href="/admin/driver_edit.php?id=<?php echo $driver["id"]; ?>" class="btn btn-secondary" style="background:#ffa000; display: inline-block; margin: 2px;">Edit</a>
          <a href="/admin/driver_delete.php?id=<?php echo $driver["id"]; ?>" class="btn btn-danger" style="display: inline-block; margin: 2px;">Delete</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>
  </div>
  
  <div class="dashboard-section">
    <h3>Routes <a href="/admin/route_add.php" class="btn btn-primary" style="float:right;">Add Route</a></h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #e0e0e0;">
      <tr style="background: #f4f6f8;"><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Name</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Start</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">End</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Bus</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Map</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Actions</th></tr>
      <?php foreach ($routes as $route): ?>
      <tr>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($route["name"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($route["start_location"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($route["end_location"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($route["number_plate"] ?? ""); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><a href="/map/route/<?php echo $route["id"]; ?>/map.php">View Map</a></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;">
          <a href="/admin/route_edit.php?id=<?php echo $route["id"]; ?>" class="btn btn-secondary" style="background:#ffa000; display: inline-block; margin: 2px;">Edit</a>
          <a href="/admin/route_delete.php?id=<?php echo $route["id"]; ?>" class="btn btn-danger" style="display: inline-block; margin: 2px;">Delete</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>
  </div>
  
  <div class="dashboard-section">
    <h3>Boarding History</h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #e0e0e0;">
      <tr style="background: #f4f6f8;"><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Student</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Bus</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Timestamp</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Action</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">GPS</th></tr>
      <?php foreach ($boarding_history as $record): ?>
      <tr>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($record["student_name"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($record["bus_number_plate"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($record["timestamp"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($record["action"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($record["gps_location"]); ?></td>
      </tr>
      <?php endforeach; ?>
    </table>
  </div>
  
  <div class="dashboard-section">
    <h3>Buses <a href="/admin/bus_add.php" class="btn btn-primary" style="float:right;">Add Bus</a></h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #e0e0e0;">
      <tr style="background: #f4f6f8;"><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Number Plate</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Driver</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Current Location</th><th style="border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left;">Actions</th></tr>
      <?php foreach ($buses as $bus): ?>
      <tr>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($bus["number_plate"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars($bus["first_name"] . " " . $bus["last_name"]); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;"><?php echo htmlspecialchars(($bus["current_latitude"] && $bus["current_longitude"]) ? $bus["current_latitude"] . ", " . $bus["current_longitude"] : "N/A"); ?></td>
        <td style="border: 1px solid #e0e0e0; padding: 8px 12px;">
          <a href="/admin/bus_edit.php?id=<?php echo $bus["id"]; ?>" class="btn btn-secondary" style="background:#ffa000; display: inline-block; margin: 2px;">Edit</a>
          <a href="/admin/bus_delete.php?id=<?php echo $bus["id"]; ?>" class="btn btn-danger" style="display: inline-block; margin: 2px;">Delete</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>
  </div>
</div>
<style>
.admin-dashboard { max-width: 1200px; margin: 30px auto; }
.dashboard-section { background: #fff; margin: 30px 0; padding: 20px 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
h2, h3 { color: #1976d2; text-align: left; }
</style>
';

include TEMPLATES_PATH . '/base.php';