Bro, here's the **complete usage guide** for both sides — like a user manual you can actually hand to someone. 📖

---

# 📘 KINSALI LOANS – COMPLETE USAGE GUIDE

---

# 🧑 USER GUIDE

## 📍 Step 1: Create Account

**URL:** `/accounts/register/`

1. Go to **Homepage** → Click **"Apply Now"** or **"Register"**
2. Fill in the form:
   - **Account Details:** Username, Email, Password
   - **Personal Info:** Phone, DOB, NIN (14 chars), Employment, Income
   - **Address:** Residential address, City, State
   - **Documents:** Upload profile picture + National ID image
   - **Payment Details:** 
     - Mobile Money number + network (MTN/Airtel)
     - Preferred disbursement method
     - Bank details (optional)
3. Click **"Create Account"**

✅ **Result:** Account created, status = **PENDING VERIFICATION**

---

## 📍 Step 2: Wait for Verification

**URL:** `/dashboard/`

1. Log in → Dashboard shows **Verification Status** card:
   - 🔴 ID Pending
   - 🔴 Photo Missing (if not uploaded)
   - 🟡 Pending Review

2. **You CANNOT apply for a loan until verified** by admin

✅ **Result:** Admin reviews your documents and either verifies or rejects

---

## 📍 Step 3: Apply for a Loan (After Verification)

**URL:** `/dashboard/` → Click **"Apply Now"** or **"New Loan"**

1. Click **"Apply Now"** button
2. Select loan product (e.g., "Personal Loan")
3. Enter:
   - **Amount** (within min/max for that product)
   - **Tenure** (months)
   - **Purpose** of loan
4. Click **"Submit Application"**

✅ **Result:** Loan created with status = **PENDING**

---

## 📍 Step 4: Track Application Status

**URL:** `/dashboard/` → **"Loan History"** table

| Status | Meaning |
|--------|---------|
| 🟡 PENDING | Waiting for admin review |
| 🟢 APPROVED | Approved — money will be sent |
| 🔵 DISBURSED | Money sent to you |
| 🔴 REJECTED | Not approved (see reason) |
| 🟢 COMPLETED | Fully repaid ✅ |

Click the 👁️ **eye icon** to see full details.

---

## 📍 Step 5: Receive Money

**URL:** `/loan/<id>/`

Once admin disburses:

1. You'll see **"How You Received Your Loan"** card:
   - Method (Mobile Money/Bank)
   - Transaction Reference
   - Date

2. Money will arrive in your MoMo/Bank

✅ **Result:** Loan status = **DISBURSED**

---

## 📍 Step 6: View Repayment Schedule

**URL:** `/loan/<id>/`

Once admin generates schedule:

1. **Next Payment Alert** (blue/red card):
   - Amount due
   - Due date
   - Days remaining

2. **Balance Overview** (4 cards):
   - Total Loan
   - Total Paid
   - Balance Remaining
   - Progress %

3. **Repayment Schedule Table:**
   - Each installment with due date, amount, status
   - Progress bar shows % completed

✅ **Result:** You know exactly what to pay and when

---

## 📍 Step 7: Send Money (Manual Payment)

**URL:** `/loan/<id>/` → **"How to Pay"** card

1. See **your business MoMo/Bank details**:
   ```
   📱 Mobile Money: 0772 123 456
   Name: Kinsali Loans Ltd
   Reference: LOAN-5
   
   🏦 Bank: Stanbic | 9030012345678
   ```

2. Open MTN/Airtel app → Send money to that number
3. Use **LOAN-{id}** as reference
4. Get SMS confirmation with **transaction ID**

---

## 📍 Step 8: Submit Payment Notice

**URL:** `/loan/<id>/` → **"I've Made a Payment"** form

1. Scroll to green card **"I've Made a Payment"**
2. Fill in:
   - **Amount Paid:** e.g., 100
   - **Payment Method:** Mobile Money / Bank / Cash
   - **Transaction ID:** e.g., MMO123456
   - **Notes:** (optional)
3. Click **"Submit Payment Notice"**

✅ **Result:** Submission appears in "Your Payment Submissions" with **⏳ PENDING** badge

---

## 📍 Step 9: Wait for Admin Approval

Once admin approves:

1. Your notice shows **✅ APPROVED**
2. Payment auto-applies to oldest unpaid installment
3. Balance updates in real-time
4. If final payment → loan becomes **COMPLETED** 🎉

---

## 📍 Step 10: Track Progress

**URL:** `/dashboard/` and `/loan/<id>/`

**On Dashboard:**
- 🔴 Overdue alert (if any payment late)
- 🔵 Next payment card
- 📅 Upcoming payments table

**On Loan Detail:**
- Updated balance cards
- Progress bar (% complete)
- Payment breakdown per installment

✅ **Result:** You always know your status

---

# 👨‍💼 ADMIN GUIDE

## 📍 Step 1: Login to Admin Panel

**URL:** `/admin-panel/login/`

1. Enter admin credentials
2. Redirects to `/admin-panel/` dashboard

---

## 📍 Step 2: Review Dashboard Stats

**URL:** `/admin-panel/`

Dashboard shows:
- Total pending loans
- Total approved loans
- Total disbursed loans
- Total rejected loans
- **Payment Notices badge** (pending count)
- Total disbursed amount ($)

---

## 📍 Step 3: Verify User Documents

**URL:** `/admin-panel/verifications/`

1. See lists:
   - 🟡 **Pending Users** – Need review
   - 🟢 **Verified Users** – Approved
   - 🔴 **Rejected Users** – Declined

2. Click a pending user → Review:
   - Profile picture
   - National ID image
   - Personal info

3. Click:
   - ✅ **Verify** → User can now apply for loans
   - ❌ **Reject** → Enter reason

✅ **Result:** User's dashboard updates with verification status

---

## 📍 Step 4: Manage Loan Products

**URL:** `/admin-panel/products/`

1. See all products (active + inactive)
2. Click **"Add Product"** to create new:
   - Name, description
   - Min/max amount
   - Interest rate
   - Min/max tenure
   - Processing fee
   - Active status

3. **Edit** or **Delete** existing products

---

## 📍 Step 5: Review Loan Applications

**URL:** `/admin-panel/` → Click pending loan

Left column shows:
- Loan info (amount, tenure, EMI)
- Applicant info (name, contact, credit score)
- Address

Right column → Actions:

### To Approve:
1. Adjust **Amount Approved** (optional, defaults to requested)
2. Add approval notes
3. Click **"Approve Loan"**

### To Reject:
1. Enter **rejection reason** (required)
2. Add internal notes
3. Click **"Reject Loan"**

✅ **Result:** Loan status updates, user sees on dashboard

---

## 📍 Step 6: Disburse Money

**URL:** `/admin-panel/loan/<id>/` (for APPROVED loans)

Right column shows:

1. **User Payment Details** (green box):
   - Their Mobile Money number + network
   - Their bank details

2. **Disbursement Form:**
   - Method: Mobile Money / Bank / Cash
   - Reference/Transaction ID
   - Notes

**Process:**
1. **Open MTN/Airtel app on your phone**
2. Send money to user's number shown in green box
3. Get your confirmation SMS with transaction ID
4. **Come back to system** → Fill form:
   - Method: Mobile Money
   - Reference: (paste transaction ID)
   - Notes: Any remarks
5. Click **"Confirm Disbursement"**

✅ **Result:** Loan status = **DISBURSED**

---

## 📍 Step 7: Generate Repayment Schedule

**URL:** `/admin-panel/loan/<id>/`

1. Click **"Generate Schedule"** button
2. System creates monthly installments based on:
   - Total repayment ÷ tenure
   - Starting from today + 1 month

✅ **Result:** Repayment table appears on left column with all installments

---

## 📍 Step 8: Record Direct Payments (Optional)

**URL:** `/admin-panel/loan/<id>/` → Repayment table

If user pays **without** submitting a notice:

1. Find the installment row
2. Enter **amount received** in the input field
3. Click **"Record"**

**Supports:**
- **Full payment** → installment marked PAID ✅
- **Partial payment** → installment marked PARTIAL (blue)
- **Multiple partials** → accumulates over time

✅ **Result:** Balance updates, user dashboard refreshes

---

## 📍 Step 9: Review Payment Notices

**URL:** `/admin-panel/payment-notices/`

See 3 sections:

### ① Pending Notices (Top priority)
Table shows:
- User + Loan #
- Amount claimed
- Transaction ID
- Submitted date

**Actions:**
- ✅ **Approve** → Auto-applies FIFO to schedule
- ❌ **Reject** → Enter reason (user sees it)

### ② Recently Approved (History)
### ③ Recently Rejected (History)

---

## 📍 Step 10: Approve Payment Notice

**URL:** `/admin-panel/payment-notices/` → Click **Approve**

**Before approving:**
1. Check your MoMo/Bank account
2. Verify the transaction ID matches
3. Confirm amount received

**Then:**
1. Click **✅ Approve** → confirm popup
2. System AUTO:
   - Marks notice as APPROVED
   - Applies amount to oldest unpaid installment (FIFO)
   - If overpayment → applies to next installment too
   - If all paid → loan status = **COMPLETED** 🎉

---

## 📍 Step 11: Reject Payment Notice

**URL:** Same page → Click **❌ Reject**

1. Modal opens asking for reason
2. Enter reason (e.g., "Transaction ID not found in our records")
3. Click **Reject Notice**

✅ **Result:** User sees REJECTED with reason, can resubmit

---

# 🔄 COMPLETE LIFECYCLE EXAMPLE

## Scenario: User Timo takes a $500 loan

| Step | Who | Action | Status |
|------|-----|--------|--------|
| 1 | Timo | Registers with docs | PENDING VERIFICATION |
| 2 | Admin | Verifies Timo | VERIFIED ✅ |
| 3 | Timo | Applies for $500, 5 months | PENDING |
| 4 | Admin | Approves with $500 | APPROVED |
| 5 | Admin | Sends $500 to Timo's MoMo | DISBURSED |
| 6 | Admin | Generates schedule (5 × $100) | Schedule created |
| 7 | Timo | Sees schedule on dashboard | 5 pending payments |
| 8 | Timo | Sends $100 via MTN | (money arrives in biz account) |
| 9 | Timo | Submits notice: $100, MMO111 | PENDING |
| 10 | Admin | Verifies MMO111 in account | ✅ Confirmed |
| 11 | Admin | Approves notice | Payment #1 = PAID |
| 12 | Timo | Sends $150 extra | (arrives) |
| 13 | Timo | Submits notice: $150, MMO222 | PENDING |
| 14 | Admin | Approves | #2 PAID, #3 partial $50 |
| 15 | Timo | Sends $250 to finish | (arrives) |
| 16 | Timo | Submits notice: $250, MMO333 | PENDING |
| 17 | Admin | Approves | #3 PAID, #4 PAID, #5 partial |
| 18 | Timo | Sends final $100 | (arrives) |
| 19 | Timo | Submits notice: $100, MMO444 | PENDING |
| 20 | Admin | Approves | All paid → **COMPLETED** 🎉 |

---

# 📋 QUICK REFERENCE CARDS

## 🧑 For Users

| Task | URL |
|------|-----|
| Register | `/accounts/register/` |
| Login | `/accounts/login/` |
| Dashboard | `/dashboard/` |
| Apply for Loan | `/dashboard/` → "Apply Now" |
| View Loan Detail | `/loan/<id>/` |
| Submit Payment | `/loan/<id>/` → "I've Made a Payment" |
| Contact Support | `/contact/` |

## 👨‍💼 For Admins

| Task | URL |
|------|-----|
| Login | `/admin-panel/login/` |
| Dashboard | `/admin-panel/` |
| Verify Users | `/admin-panel/verifications/` |
| Manage Products | `/admin-panel/products/` |
| Review Loan | `/admin-panel/loan/<id>/` |
| **Payment Notices** | `/admin-panel/payment-notices/` |

---

# 🚨 IMPORTANT RULES

| Rule | Description |
|------|-------------|
| **Verify First** | Users must be verified before applying |
| **Manual Everything** | Admin sends/receives money manually via MoMo/Bank |
| **FIFO** | Payments apply to oldest installment first |
| **Auto-Complete** | Loan completes when all installments paid |
| **Audit Trail** | Every payment notice is logged forever |
| **Reference Format** | Always use LOAN-{id} as payment reference |

---

**Bro, save this as `USAGE_GUIDE.md`** in your project. Now you have:
- 📋 `PROJECT_DOCUMENTATION.md` (technical)
- 📖 `USAGE_GUIDE.md` (how to use)

Hand these to anyone joining your team and they'll be productive immediately! 💪

Ready to build **Email Notifications** next? 🚀