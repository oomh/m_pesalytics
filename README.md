# 💸 M-pesalytics: Your Personal M-Pesa Statement Analyzer

Hey there! Welcome to **M-pesalytics** - your friendly companion for understanding where your M-Pesa money actually goes.

Ever wondered why your M-Pesa balance seems to disappear faster than you can say "Lipa Na M-Pesa"? You're not alone! M-pesalytics turns your confusing PDF statements into clear, visual insights that actually make sense.

## 🚀 Let's Get Started

Ready to dive into your spending habits? Here's how to get rolling:

### Step 1: Get Your Statement

- Head over to the M-Pesa app, MySafaricom app or dial `*334#`
- Request your statement for the period you want to analyze. Longer periods are better because M-pesalytics allows you to filter by date
- Safaricom will send you a password-protected PDF via email, or a non-password-protected PDF if you get it from the M-Pesa app.

### Step 2: Fire Up M-pesalytics

Visit the app at: **<https://m-pesalytics.streamlit.app/>**

### Step 3: Upload and Explore

1. **Upload your PDF** - Just drag and drop or click to browse
2. **Enter your password** - The one Safaricom sent you, or leave it blank if you got a non-password-protected PDF
3. **Hit "Process"** - Watch the magic happen!
4. **Explore your data** - Use the tabs to see different transaction types
5. **Filter by date** - Focus on specific months or date ranges with the filters in the sidebar

That's it! No complicated setup, no account creation, just pure financial insight.

## 💡 What You'll Discover

### 🛒 **Lipa Na M-Pesa Transactions**

- **Buy Goods**: See exactly which shops and services you spend most at
- **Pay Bill**: Track your utility bills, subscriptions, and service payments
- **Pochi La Biashara**: Small business payments and local vendors

### 💰 **Money Movement**

- **Transfers**: Who you're sending money to and how often
- **Received Money**: Track income from friends, family, or business
- **Cash Withdrawals**: Your favorite agents and withdrawal patterns

### 📱 **Mobile Services**

- **Airtime & Bundles**: Your mobile spending breakdown
- **Deposits**: Money coming into your account from various sources

### 🔍 **Interactive Features**

- **Click any merchant** to see individual transaction details
- **Use date filters** to focus on specific time periods
- **Expand sections** to see your complete transaction history
- **Visual charts** make patterns easy to spot

## 🏢 Got a Business Account?

If you're using M-Pesa for business (SME accounts with Lipa Na M-Pesa), M-pesalytics works great for you too! Your business transactions will show up in the analysis, helping you understand customer payment patterns, popular payment times, and transaction volumes.  -->

**Pro tip**: Business accounts often have mixed personal and business transactions - that's totally normal!

## ⚠️ A Friendly Heads-Up


**About Categorization**: Sometimes M-pesalytics might get a little confused about how to categorize certain transactions - that's completely normal! The smart categorization does its best, but M-Pesa transaction descriptions can be tricky.


**Don't worry though!** 🎯 If something looks off, just click on the expandable sections (like "All Buy Goods Transactions") to see the complete, unfiltered data. This way you can always verify and understand exactly what each transaction was.

**For SME Users**: Business transactions might occasionally get mixed up with personal categories, but again, the expandable sections will show you everything clearly.

## 🔒 Your Privacy Matters

- **100% Local Processing**: Your data never leaves your device
- **No Storage**: We don't save your statements or passwords anywhere
- **No Accounts**: No sign-ups, no personal info required
- **Session-Based**: Everything clears when you close your browser or refresh the page


**Note**: Since I haven't been able to access a comprehensive list of M-Pesa transaction types, some categories are hardcoded. If you find any missing or incorrect categories, please let me know so I can update them.

## 🚧 Known Quirks

- **Large Files**: Really big statements (6+ months) might take a moment to process
- **PDF Variations**: Some older statement formats might look a bit different
- **Browser Compatibility**: Works best on Chrome, Firefox, or Safari

## 🆘 Need Help?

**PDF Won't Upload?**


- Make sure it's the official M-Pesa statement from Safaricom
- Check that you're using the correct password

**Weird Categories?**


- Check the expandable sections for the full transaction list
- Remember that M-Pesa descriptions can be cryptic!

**Missing Transactions?**

- Some very old transaction formats might not be recognized
- The expandable sections will show you what was processed

## 🤝 Let's Make It Better

Found a bug? Have a suggestion? I'd love to hear from you! M-pesalytics is a work in progress, and your feedback helps make it better for everyone.

## **Disclaimer**

M-pesalytics is for personal financial analysis only. While we do our best to categorize transactions accurately, always double-check important financial decisions against your official M-Pesa records.

You're responsible for keeping your data secure and ensuring compliance with any local data protection regulations that might apply to you.

AI aided the development of this app, I used it to generate doc strings, type hints, and some comments, critiqued my code, checked my grammar(especially in this README.md) and helped me rearrange functions and methods when my code got long and confusing. In the next phase, I plan to use AI for cleaning up my unit tests (not uploaded) and adding logging functionality.

---

**Ready to discover your spending patterns?**

Launch M-pesalytics *<https://m-pesalytics.streamlit.app/>* and start exploring! 🚀
