# Vehicle Parking System - Project Abstract

## Project Overview

The **Vehicle Parking System** is a comprehensive Django-based web application designed to manage parking operations across multiple mall locations. The system integrates multiple user roles with distinct functionalities, payment processing capabilities, and real-time parking slot management. It enables parking reservations, online payments, rate management, and booking history tracking.

---

## User Types & Their Functionalities

### 1. **Regular Users (Customers)**
**Type ID: 1** | **Model: User (is_customer=1)**

#### Key Functionalities:
- **Account Management**: Registration and login with admin approval process
- **Wallet/Balance System**: 
  - Recharge account balance through payment gateway (Stripe/Razorpay)
  - Maintain minimum balance (Rs. 500 required) to book parking
  - Track balance and recharge history
- **Parking Slot Search & Booking**:
  - Browse available parking slots by location and mall
  - Filter slots by vehicle type (Car/Bike)
  - Select date/time range for booking
  - Book slots with real-time availability checking
  - Generate unique QR code for each booking
- **Booking Management**:
  - View upcoming reservations
  - Track booking history
  - Monitor booking status (Reserved → Occupied → Completed)
  - View reserved booking count
- **Payment Integration**:
  - Online payment for parking using Stripe/Razorpay
  - View transaction history
  - Auto-approval of payments

#### Database Model:
```
User → Booking (one-to-many)
User → Recharge (one-to-many) 
User → Customer (one-to-one profile)
```

#### Peculiarities:
- Users must have admin approval before account activation
- Mandatory minimum balance requirement for slot booking
- QR code generation for each booking
- Booking data stored with unique constraints on parking slot + time range

---

### 2. **Mall/Parking Lot Administrators**
**Type ID: 2** | **Model: User (is_customer=2) + Mall + Staff**

#### Key Functionalities:
- **Parking Slot Management**:
  - Add/Create new parking slots with slot numbers
  - Define vehicle types per slot (Car/Bike)
  - Set location within parking facility
  - Edit and delete existing slots
  - View all managed parking slots
- **Rate Management**:
  - Set hourly rates for different vehicle types
  - Set daily rates for different vehicle types
  - Edit rate structures
  - Delete outdated rates
  - Prevent duplicate rates for same vehicle type
- **Transaction Monitoring**:
  - View total revenue earned
  - Track payment transactions
  - Access detailed transaction history with filters
  - View booking history by date range
  - Monitor today's booked slots
- **Staff Management**:
  - Create supervisor/staff accounts
  - Assign staff to specific mall
  - Manage staff permissions

#### Database Model:
```
Mall (Profile) ← User (main account)
      ↓
  ParkingSlot (multiple)
  Rate (multiple by vehicle type)
  Location (zone reference)
  Staff (supervisors)
      ↓
  Booking (child through ParkingSlot)
```

#### Peculiarities:
- Mall account requires admin approval before activation
- Unique slots numbering across system
- Rate-based pricing with hourly and daily options
- Separate supervisor/staff role assignment
- Real-time booking status tracking tied to payment

---

### 3. **Supervisors/On-Site Staff**
**Type ID: 3** | **Model: User (is_customer=3) + Staff**

#### Key Functionalities:
- **Daily Slot Monitoring**:
  - View today's booked parking slots
  - Track vehicle information per booking
  - Monitor booking status in real-time
  - Check start/end times for each booking
- **QR Code Verification**:
  - Scan and verify QR codes for entry/exit
  - OpenCV integration for QR code reading
  - Update booking status based on verification
- **Booking Oversight**:
  - View all bookings for assigned mall
  - Track booking progression (Reserved → Occupied → Completed)
  - Monitor payment status

#### Database Model:
```
Staff → User (account)
    ↓
  Mall (assigned location)
    ↓
  Booking (view through ParkingSlot)
```

#### Peculiarities:
- Supervisor must be approved before account activation
- Linked to specific mall through Staff model
- Uses OpenCV/QR scanning for on-site verification
- Real-time timezone-aware time formatting (IST +5:30)
- Only views bookings for assigned mall

---

### 4. **Super Admin**
**Type: Django Superuser** | **Model: User (is_superuser=True)**

#### Key Functionalities:
- **User Approval System**:
  - View pending users awaiting approval
  - Approve regular user accounts
  - Reject and delete pending accounts
  - View active approved users
- **Mall Registration Management**:
  - Review pending mall registrations
  - Approve/Reject mall operators
  - Manage mall accounts
- **System Configuration**:
  - Manage locations in the system
  - Add/remove parking zones
  - Overall system oversight
- **Django Admin Panel**:
  - Full database access
  - Manage all models
  - User role assignment
  - Rate and pricing oversight

#### Peculiarities:
- Only superuser can access approval workflows
- Controls initial activation of user accounts
- Central point for system configuration
- No approval needed for their own account

---

## Key System Features

### 1. **Booking Management**
- **Status Flow**: Reserved → Occupied → Completed
- **Unique Constraints**: Prevents double-booking (slot + start_time + end_time)
- **QR Code Integration**: Auto-generated unique QR code per booking
- **Time Management**: IST timezone handling (+5:30 offset)

### 2. **Payment Processing**
- **Gateway Integration**: Stripe (Primary) with Razorpay fallback
- **Wallet System**: Prepaid balance model
- **Transaction Recording**: Tracks paid_amount per booking
- **Balance Validation**: Minimum Rs. 500 required

### 3. **Parking Slot Management**
- **Status Tracking**: 
  - 0 = Free
  - 1 = Booked
  - 2 = Allocated
  - 3 = Paid
- **Vehicle Type Support**: Car and Bike
- **Location Zones**: Multiple location IDs per parking facility
- **Rate Structure**: Hourly and daily pricing per vehicle type

### 4. **Real-time Availability Checking**
- Database queries check overlapping bookings
- Status = 'reserved' filter for availability
- Dynamic slot list generation based on date range

### 5. **Multi-Mall Support**
- Multiple independent parking facilities
- Location-based mall filtering
- Hierarchical location → mall → slot structure

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Django 4.2.16 |
| **Database** | SQLite (development) |
| **Frontend** | HTML/CSS/JavaScript |
| **Build Tool** | Gulp |
| **Image Processing** | OpenCV 4.10 |
| **QR Code** | qrcode 7.4.2 |
| **Payment Gateways** | Stripe, Razorpay |
| **Date Handling** | python-dateutil |
| **Server** | ASGI (Daphne support via asgiref) |

---

## Data Flow Diagram

```
┌─────────────┐
│   Users     │
│ (is_cust=1) │
└──────┬──────┘
       │
       │ Creates
       ↓
┌──────────────────┐
│    Booking       │ → ParkingSlot → Mall → Location
│  + QR Code       │
│  + Status        │
│  + paid_amount   │
└──────┬───────────┘
       │
       │ Payment
       ↓
┌──────────────────┐
│   Stripe/        │
│  Razorpay        │
│  Payment Gateway │
└──────────────────┘

┌─────────────┐
│   Malls     │
│(is_cust=2)  │ Creates → ParkingSlot
└─────────────┘       └→ Rate

┌─────────────┐
│ Supervisors │
│(is_cust=3)  │ Views → Booking (QR Scan)
└─────────────┘
       │ Assigned to
       ↓
     Mall
```

---

## Session Management

The system uses Django session middleware to track:
- `user_id`: Regular user identifier
- `mall_id`: Mall administrator identifier
- `staff_id`: Supervisor/staff identifier
- `uname`: Display name (first_name + last_name)
- `balance`: Current wallet balance

---

## Peculiarities & Notable Design Decisions

1. **Custom User Type System**: Uses `is_customer` integer field (1=User, 2=Mall, 3=Staff) instead of Django groups
2. **Session-Based Authorization**: Relies on session variables rather than permission system
3. **Approval Workflow**: Users inactive by default until super admin approval
4. **Dual Payment Integration**: Both Stripe and Razorpay support in dependencies
5. **QR Code for Entry/Exit**: OpenCV-based scanning for supervisor verification
6. **Timezone Handling**: Hard-coded +5:30 offset for IST instead of Django timezone framework
7. **Alert System**: Uses JavaScript window.alert for user notifications
8. **No Explicit Role/Permission Model**: Custom logic in views for role checking
9. **Prepaid Model**: Users must maintain minimum balance before booking
10. **Rate Flexibility**: Separate hourly and daily rates per vehicle type per mall

---

## Security Notes

⚠️ **Areas for Improvement**:
- Stripe API key exposed in source code
- DEBUG = True in production settings
- CSRF exemptions on some views
- Session-based auth not as robust as Django permission system
- No input validation/sanitization shown in views
- SQL injection potential with raw queries (if used elsewhere)

---

## Workflow Summary

### User Journey:
1. Register → Pending Approval → Approved → Login
2. Recharge Wallet → View Slots → Book Slot → Pay → Receive QR
3. Supervisor Scans QR → Status Changes → Booking Completion

### Mall Journey:
1. Register → Pending Approval → Approved → Login
2. Add Parking Slots → Set Rates → Monitor Bookings → View Revenue

### Supervisor Journey:
1. Registration by Mall → Pending Approval → Approved → Login
2. View Today's Bookings → Scan QR Codes → Verify Entry/Exit

---

**Project Status**: Development Phase with Payment Integration  
**Last Updated**: May 2026
