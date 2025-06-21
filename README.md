# 🚗 CarRental – Car Rental Management System

CarRental is a web-based management system built with **Django** and **MongoDB** designed for car rental agencies. It enables smooth operation for managing vehicles, clients, reservations, and user accounts (Managers and Administrators) through a clean and modern interface.

---

## 📌 Features

### 👤 User Roles

- **Administrator**
  - Add, edit, and delete Manager accounts.
  - Secure access via authentication.

- **Manager**
  - View and manage the car fleet.
  - Create and manage client records.
  - Make, accept, or refuse car reservations.
  - Access reservation history and client overviews.

### 🚘 Car Management

- Add, edit, and delete cars.
- Upload images and input detailed specifications (brand, type, transmission, price/day, etc.).
- Filter cars by name, price, and availability.

### 📅 Reservation Management

- View pending reservations.
- Confirm or cancel bookings.
- Track reservation history.
- Automatically calculate total rental price based on duration and car price.

### 👥 Client Management

- Add, edit, or delete clients.
- Track number of reservations per client.
- Search clients by name or CIN.

---

## 🛠️ Technologies Used

- **Backend**: Django (Python)
- **Database**: MongoDB (via Djongo)
- **Frontend**: HTML5, Bootstrap 4, SB Admin 2
- **Templating**: Django Templates