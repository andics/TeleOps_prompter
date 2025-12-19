# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Python Dependencies

**Option A: Using Conda (Recommended for this project)**
```bash
conda create -n teleops_prompter python=3.10 -y
conda activate teleops_prompter
pip install -r requirements.txt
```

**Option B: Using pip directly**
```bash
pip install -r requirements.txt
```

## Step 2: Set Your OpenAI API Key

**Option A: Using .env file (Recommended)**
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

**Option B: Environment Variable**
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-actual-key-here"
```

## Step 3: Update Camera URL (if needed)

If your camera is at a different address, edit `app.py` line 108:
```python
camera_url="http://YOUR_IP:PORT/cam_c"
```

## Step 4: Run the Application

**Windows (using the automated script):**
```cmd
run.bat
```
This will automatically create/activate the Conda environment `teleops_prompter` and run the app.

**Or manually:**
```bash
conda activate teleops_prompter
python app.py
```

## Step 5: Open in Browser

Navigate to: **http://localhost:5000**

## Step 6: Add Your First Filter

In the middle panel, enter a prompt like:
```
Is there a person in this photo? Respond only True for Yes and False for No.
```

Click **"Add Filter"** and watch it evaluate!

## Keyboard Shortcuts

- **Ctrl + Enter** in filter input: Add filter
- **Ctrl + Enter** in chat input: Send message

## Tips

- The switch on each filter shows the result (Green = True, Red = False)
- Toggle the switch to enable/disable a filter
- Use ↑↓ buttons to reorder filters
- Click × to remove a filter
- Toggle theme with the sun/moon button (top right)

## Troubleshooting

**No frames appearing?**
- Check if camera URL is accessible in your browser
- Verify the IP address and port

**OpenAI errors?**
- Verify your API key is correct
- Check you have API credits available

**Slow performance?**
- Reduce number of active filters
- Increase capture interval in `app.py`

## Example Filters to Try

```
Is there a bottle in this image? Respond only True for Yes and False for No.

Are there more than 2 people visible? Respond only True for Yes and False for No.

Is the light on? Respond only True for Yes and False for No.

Is there text visible in this image? Respond only True for Yes and False for No.
```

Enjoy monitoring your camera feed with AI! 🚀

