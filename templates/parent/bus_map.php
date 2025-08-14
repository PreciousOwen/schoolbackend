<?php
$content = '
<div class="dashboard-container">
  <h2 class="dashboard-title">Bus Locations</h2>
  <div class="card">
    <h3>Children\'s Buses</h3>
    <?php if (empty($buses)): ?>
      <p>No buses found for your children.</p>
    <?php else: ?>
      <table class="styled-table">
        <thead>
          <tr>
            <th>Child Name</th>
            <th>Bus Number Plate</th>
            <th>Current Location</th>
          </tr>
        </thead>
        <tbody>
          <?php foreach ($buses as $bus_info): ?>
          <tr>
            <td><?php echo htmlspecialchars($bus_info["student"]["name"]); ?></td>
            <td><?php echo htmlspecialchars($bus_info["bus"]["number_plate"]); ?></td>
            <td>
              <?php if ($bus_info["bus"]["current_latitude"] && $bus_info["bus"]["current_longitude"]): ?>
                <?php echo htmlspecialchars($bus_info["bus"]["current_latitude"] . ", " . $bus_info["bus"]["current_longitude"]); ?>
              <?php else: ?>
                <span class="text-muted">Location not available</span>
              <?php endif; ?>
            </td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    <?php endif; ?>
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