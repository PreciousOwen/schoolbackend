<?php
$content = '
<div class="dashboard-container">
  <h2 class="dashboard-title">Parent Dashboard</h2>
  <div class="card">
    <h3>Your Children</h3>
    <table class="styled-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>RFID</th>
          <th>Route</th>
          <th>Map</th>
        </tr>
      </thead>
      <tbody>
        <?php foreach ($children as $child): ?>
        <tr>
          <td><?php echo htmlspecialchars($child["name"]); ?></td>
          <td><?php echo htmlspecialchars($child["rfid"]); ?></td>
          <td><?php echo isset($child["route"]) ? htmlspecialchars($child["route"]["name"]) : \'<span class="text-muted">No route assigned</span>\'; ?></td>
          <td>
            <?php if (isset($child["route"])): ?>
              <a href="/map/student/<?php echo $child["id"]; ?>/map.php" class="btn btn-primary">View Map</a>
            <?php else: ?>
              <span class="text-muted">N/A</span>
            <?php endif; ?>
          </td>
        </tr>
        <?php endforeach; ?>
      </tbody>
    </table>
  </div>
  <div class="card" style="margin-top: 32px;">
    <a href="/parent/bus_map.php" class="btn btn-secondary">View All Bus Locations</a>
  </div>
</div>
<style>
.dashboard-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 24px;
}
.dashboard-title {
  color: var(--primary);
  margin-bottom: 24px;
}
.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 24px;
  margin-bottom: 24px;
}
.styled-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}
.styled-table th, .styled-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}
.styled-table th {
  background: var(--background);
  color: #333;
}
</style>
';

include TEMPLATES_PATH . '/base.php';