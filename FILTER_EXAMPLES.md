# Vision Filter Examples

A collection of example prompts you can use with the Camera Feed Monitor application.

## Basic Object Detection

### Presence Detection
```
Is there a bottle in this image? Respond only True for Yes and False for No.
```

```
Is there a person visible in this photo? Respond only True for Yes and False for No.
```

```
Is there a car in this image? Respond only True for Yes and False for No.
```

```
Is there a phone visible in this photo? Respond only True for Yes and False for No.
```

### Specific Object Features
```
Is there a cap on the bottle in this photo? Respond only True for Yes and False for No.
```

```
Is the door open in this image? Respond only True for Yes and False for No.
```

```
Is the light turned on? Respond only True for Yes and False for No.
```

```
Is the laptop screen on? Respond only True for Yes and False for No.
```

## Counting and Quantity

```
Are there more than 2 people visible? Respond only True for Yes and False for No.
```

```
Are there more than 3 objects on the table? Respond only True for Yes and False for No.
```

```
Is there exactly one bottle visible? Respond only True for Yes and False for No.
```

```
Are there any people in the background? Respond only True for Yes and False for No.
```

## Color Detection

```
Is there a red object in this image? Respond only True for Yes and False for No.
```

```
Is the car in this photo blue? Respond only True for Yes and False for No.
```

```
Is there anything green visible? Respond only True for Yes and False for No.
```

```
Is the light showing red? Respond only True for Yes and False for No.
```

## Position and Location

```
Is there a person on the left side of the image? Respond only True for Yes and False for No.
```

```
Is there an object in the center of the frame? Respond only True for Yes and False for No.
```

```
Is the bottle on the table? Respond only True for Yes and False for No.
```

```
Is someone standing near the door? Respond only True for Yes and False for No.
```

## State and Condition

```
Is the room well-lit? Respond only True for Yes and False for No.
```

```
Is it daytime in this image? Respond only True for Yes and False for No.
```

```
Is the workspace clean and organized? Respond only True for Yes and False for No.
```

```
Is there motion blur in this image? Respond only True for Yes and False for No.
```

## Safety and Security

```
Is there a person wearing a safety helmet? Respond only True for Yes and False for No.
```

```
Is the emergency exit visible and clear? Respond only True for Yes and False for No.
```

```
Is anyone wearing a face mask? Respond only True for Yes and False for No.
```

```
Is there a fire extinguisher visible? Respond only True for Yes and False for No.
```

## Text and Signage

```
Is there text visible in this image? Respond only True for Yes and False for No.
```

```
Is there a stop sign visible? Respond only True for Yes and False for No.
```

```
Is there a warning sign in the image? Respond only True for Yes and False for No.
```

```
Is there a label on the bottle? Respond only True for Yes and False for No.
```

## Activity Detection

```
Is someone using a computer? Respond only True for Yes and False for No.
```

```
Is anyone eating or drinking? Respond only True for Yes and False for No.
```

```
Is someone on a phone call? Respond only True for Yes and False for No.
```

```
Is there any movement in this image? Respond only True for Yes and False for No.
```

## Manufacturing and Quality Control

```
Is the product properly aligned? Respond only True for Yes and False for No.
```

```
Is there a defect visible on the surface? Respond only True for Yes and False for No.
```

```
Is the assembly complete? Respond only True for Yes and False for No.
```

```
Are all components present? Respond only True for Yes and False for No.
```

## Retail and Inventory

```
Is the shelf fully stocked? Respond only True for Yes and False for No.
```

```
Is there a price tag visible? Respond only True for Yes and False for No.
```

```
Is the product display neat? Respond only True for Yes and False for No.
```

```
Are there empty spaces on the shelf? Respond only True for Yes and False for No.
```

## Environmental Monitoring

```
Is it raining in this image? Respond only True for Yes and False for No.
```

```
Is there snow visible? Respond only True for Yes and False for No.
```

```
Is the sky cloudy? Respond only True for Yes and False for No.
```

```
Is there water on the floor? Respond only True for Yes and False for No.
```

## Animal Detection

```
Is there a dog in this image? Respond only True for Yes and False for No.
```

```
Is there a cat visible? Respond only True for Yes and False for No.
```

```
Are there any birds in the photo? Respond only True for Yes and False for No.
```

```
Is there any animal visible? Respond only True for Yes and False for No.
```

## Equipment and Tools

```
Is there a hammer visible? Respond only True for Yes and False for No.
```

```
Is the machine running? Respond only True for Yes and False for No.
```

```
Is there a tool on the workbench? Respond only True for Yes and False for No.
```

```
Is the equipment properly stored? Respond only True for Yes and False for No.
```

## Advanced Combinations

### Multiple Conditions
```
Is there a person AND are they wearing a helmet? Respond only True for Yes and False for No.
```

```
Is the door open AND is there someone near it? Respond only True for Yes and False for No.
```

```
Is it daytime AND is the light turned on? Respond only True for Yes and False for No.
```

### Negative Conditions
```
Is the area empty with no people? Respond only True for Yes and False for No.
```

```
Is there no bottle on the table? Respond only True for Yes and False for No.
```

```
Is the workspace unoccupied? Respond only True for Yes and False for No.
```

## Tips for Writing Effective Filters

### ✅ DO:
- **Be specific**: "Is there a red bottle?" vs "Is there something?"
- **Use clear language**: Simple, direct questions
- **Include the response format**: "Respond only True for Yes and False for No"
- **Focus on one thing**: One question per filter
- **Test and refine**: Adjust based on results

### ❌ DON'T:
- **Be vague**: "Is something happening?"
- **Ask multiple questions**: "Is there a bottle and is it red and is the cap on?"
- **Use ambiguous terms**: "Is it nice?" (subjective)
- **Forget the response format**: GPT-4o might give long answers
- **Use complex logic**: Keep it simple for better accuracy

## Prompt Template

Use this template for consistent results:

```
Is there [OBJECT/CONDITION] [LOCATION/QUALIFIER]? Respond only True for Yes and False for No.
```

**Examples:**
- Is there **a person** **in the frame**? Respond only True for Yes and False for No.
- Is there **a red light** **on the device**? Respond only True for Yes and False for No.
- Is there **text** **visible on the screen**? Respond only True for Yes and False for No.

## Use Case Examples

### Security Monitoring
```
1. Is there a person in the restricted area? Respond only True for Yes and False for No.
2. Is the door closed? Respond only True for Yes and False for No.
3. Is the security camera view clear? Respond only True for Yes and False for No.
```

### Production Line
```
1. Is the product properly positioned? Respond only True for Yes and False for No.
2. Is there a defect visible? Respond only True for Yes and False for No.
3. Is the assembly complete? Respond only True for Yes and False for No.
4. Is the quality control label attached? Respond only True for Yes and False for No.
```

### Office Occupancy
```
1. Is there someone at the desk? Respond only True for Yes and False for No.
2. Is the computer screen on? Respond only True for Yes and False for No.
3. Is the room occupied? Respond only True for Yes and False for No.
```

### Parking Monitoring
```
1. Is there a car in the parking spot? Respond only True for Yes and False for No.
2. Is the parking spot empty? Respond only True for Yes and False for No.
3. Is there a vehicle blocking the entrance? Respond only True for Yes and False for No.
```

### Laboratory Safety
```
1. Is anyone wearing safety goggles? Respond only True for Yes and False for No.
2. Is there an open flame visible? Respond only True for Yes and False for No.
3. Is the fume hood closed? Respond only True for Yes and False for No.
4. Is protective equipment being worn? Respond only True for Yes and False for No.
```

## Troubleshooting Filter Results

### If you get inconsistent results:

1. **Make the prompt more specific**
   - Before: "Is there something red?"
   - After: "Is there a red bottle in the center of the image?"

2. **Add context**
   - Before: "Is it on?"
   - After: "Is the desk lamp turned on?"

3. **Simplify complex questions**
   - Before: "Is there a person wearing a blue shirt and holding a phone?"
   - After: Split into two filters

4. **Adjust lighting expectations**
   - Consider: "Is the image well-lit enough to see details?"

5. **Test during different conditions**
   - Day vs night
   - Different angles
   - Various lighting

## Performance Tips

- **Start with 2-3 filters** to test the system
- **Toggle off unused filters** to save API calls
- **Group related filters** for easier management
- **Use descriptive prompts** for easier identification
- **Monitor costs** - each filter evaluation costs API credits

## Custom Filters for Your Use Case

Think about:
1. **What do you need to monitor?**
2. **What conditions trigger an alert?**
3. **What specific details matter?**
4. **How often does it change?**
5. **What actions follow a True/False result?**

Then create filters that match your specific needs!

---

**Need more examples?** The GPT-4o Vision model is very capable. Experiment with your own prompts and see what works best for your use case!

