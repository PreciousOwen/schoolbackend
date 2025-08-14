<?php
$content = '
<div class="dashboard-container">
  <h2 class="dashboard-title">Driver Dashboard</h2>
  <div class="card">
    <?php if ($bus): ?>
      <p><strong>Bus:</strong> <?php echo htmlspecialchars($bus["number_plate"]); ?></p>
    <?php endif; ?>
    <?php if ($route): ?>
      <p><strong>Route:</strong> <?php echo htmlspecialchars($route["name"]); ?><br>
      <span class="text-muted"><?php echo htmlspecialchars($route["start_location"]); ?> &rarr; <?php echo htmlspecialchars($route["end_location"]); ?></span></p>
    <?php endif; ?>
    <a href="/driver/map_redirect.php" class="btn btn-primary" style="margin-bottom: 16px;">View My Route Map</a>
  </div>
  <div class="card">
    <h3>Students on this Route</h3>
    <table class="styled-table">
      <thead>
        <tr><th>Name</th><th>RFID</th></tr>
      </thead>
      <tbody>
        <?php foreach ($students as $student): ?>
        <tr>
          <td><?php echo htmlspecialchars($student["name"]); ?></td>
          <td><?php echo htmlspecialchars($student["rfid"]); ?></td>
        </tr>
        <?php endforeach; ?>
      </tbody>
    </table>
  </div>
  <div class="card" style="margin-top: 32px;">
    <a href="/driver/bus_map.php" class="btn btn-secondary">View Live Bus Location</a>
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