import connect

mydb = connect.connect_mysql()
mycursor = mydb.cursor()

import plotly.express as px
import pandas as pd
import streamlit as st

# Configure the Streamlit page
st.set_page_config(
    page_title="LargeCo Dashboard",  # Title of the dashboard
    layout="wide",  # Use wide layout
    page_icon=":bar_chart:",  # Icon for the browser tab
    initial_sidebar_state="expanded"
)

# Add a title and logo
st.title("LargeCo Dashboard designed by Monira Alkidim & Foris Huang")
st.image("https://i.ibb.co/2kdqCDm/logo.jpg", width=1000)


# Tabs
tab1, tab2, tab3 = st.tabs(["Customers", "Products", "Employees"])

# Customers Tab
with tab1:
    st.header("Customers")

    # Most Valuable Customers Chart
    st.subheader("Most Valuable Customers")
    mycursor.execute("""
        SELECT Cust_Code, CONCAT(Cust_Fname, ' ', Cust_Lname) AS Name, Cust_Balance AS Revenue
        FROM LGCUSTOMER
        ORDER BY Cust_Balance DESC
        LIMIT 10
    """)
    # Fetch data and convert to DataFrame
    data = pd.DataFrame(mycursor.fetchall(), columns=[i[0] for i in mycursor.description])

    # Plot bar chart
    fig = px.bar(
        data,
        x="Name",
        y="Revenue",
        title="Most Valuable Customers",
        labels={"Revenue": "REVENUE", "Name": "NAME"},
    )
    fig.update_traces(marker_color="skyblue")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Customer Data Table
    with st.expander("Customer Data"):
        st.dataframe(data.style.format({"Revenue": "{:,.2f}"}))




# Products Tab
with tab2:  # Ensure this code is inside the Products tab
    st.subheader("Products Overview")

    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2)  # Correctly define col1 and col2

    # Pie Chart: Products by Brands
    with col1:
        st.subheader("Products by Brands")
        # Fetch data for the pie chart
        mycursor.execute("""
            SELECT LB.BRAND_NAME, COUNT(LP.Prod_SKU) AS NUMPRODUCTS
            FROM LGBRAND LB
            JOIN LGPRODUCT LP ON LB.BRAND_ID = LP.BRAND_ID
            GROUP BY LB.BRAND_NAME
            ORDER BY NUMPRODUCTS DESC
        """)
        product_data = pd.DataFrame(mycursor.fetchall(), columns=["BRAND_NAME", "NUMPRODUCTS"])

        # Define custom colors for the pie chart
        pie_colors = [
            "#87CEFA",  # Light Blue for Long Haul
            "#4682B4",  # Steel Blue for Home Comfort
            "#FFB6C1",  # Light Pink for Le Mode
            "#FF6347",  # Tomato Red for Binder Prime
            "#90EE90",  # Light Green for Olde Tyme Quality
            "#20B2AA",  # Light Sea Green for Stuttenfurst
            "#FFD700",  # Gold for Busters
            "#FFA500",  # Orange for Valu-Matte
            "#9370DB",  # Medium Purple for Foresters Best
        ]

        # Create pie chart
        pie_fig = px.pie(
            product_data,
            names="BRAND_NAME",
            values="NUMPRODUCTS",
            title="Products by Brands",
            color="BRAND_NAME",
            color_discrete_map=dict(zip(product_data["BRAND_NAME"], pie_colors)),  # Match colors to brands
        )

        # Display pie chart
        st.plotly_chart(pie_fig, use_container_width=True)

        # Expandable table for Brand Data
        with st.expander("Brand Data"):
            st.dataframe(
                product_data.style.format({"NUMPRODUCTS": "{:.0f}"})
            )

    # Scatter Plot: Inventory Value
    with col2:
        st.subheader("Inventory Value")
        # Fetch data for the scatter plot
        mycursor.execute("""
            SELECT LP.Prod_Description, LP.Prod_Category, LP.Prod_Price, LP.Prod_QOH
            FROM LGPRODUCT LP
        """)
        inventory_data = pd.DataFrame(mycursor.fetchall(), columns=["PROD_DESCRIPTION", "PROD_CATEGORY", "PROD_PRICE", "PROD_QOH"])

        # Ensure numeric fields are properly formatted
        inventory_data["PROD_PRICE"] = pd.to_numeric(inventory_data["PROD_PRICE"], errors="coerce")
        inventory_data["PROD_QOH"] = pd.to_numeric(inventory_data["PROD_QOH"], errors="coerce")

        # Calculate inventory value (price * quantity)
        inventory_data["INVENTORY_VALUE"] = inventory_data["PROD_PRICE"] * inventory_data["PROD_QOH"]

        # Drop rows with missing values in key columns
        inventory_data = inventory_data.dropna(subset=["PROD_PRICE", "PROD_QOH", "INVENTORY_VALUE"])

        # Define custom colors for the scatter plot
        scatter_colors = {
            "Top Coat": "#4682B4",  # Steel Blue
            "Primer": "#1E90FF",   # Dodger Blue
            "Sealer": "#D8BFD8",   # Thistle
            "Filler": "#FF6347",   # Tomato Red
            "Cleaner": "#32CD32",  # Lime Green
        }

        # Create scatter plot
        scatter_fig = px.scatter(
            inventory_data,
            x="PROD_QOH",  # Quantity on hand
            y="PROD_PRICE",  # Product price
            size="INVENTORY_VALUE",  # Bubble size
            color="PROD_CATEGORY",  # Bubble color
            hover_name="PROD_DESCRIPTION",  # Name displayed on hover
            title="Inventory Value",
            labels={"PROD_QOH": "Product Quantity on Hand", "PROD_PRICE": "Product Price"},
            size_max=20,  # Adjust maximum bubble size
            color_discrete_map=scatter_colors,  # Use custom colors for categories
        )

        # Display scatter plot
        st.plotly_chart(scatter_fig, use_container_width=True)

        # Expandable table for Inventory Data (without Inventory Value)
        with st.expander("Inventory Data"):
            # Exclude "INVENTORY_VALUE" column in the table
            inventory_table = inventory_data.drop(columns=["INVENTORY_VALUE"])
            st.dataframe(
                inventory_table.style.format({
                    "PROD_PRICE": "{:.2f}",
                    "PROD_QOH": "{:.0f}"
                })
            )



# Employees Tab - Side-by-Side Layout with Collapsible Tables
with tab3:  # Ensure this is inside the Employees tab
    st.subheader("Employees Overview")

    # Create two columns for the two charts
    col1, col2 = st.columns(2)

    # Column 1: Departments, Managers, and Employees Sunburst Chart
    with col1:
        st.subheader("Departments, Managers, and Employees")

        # Fetch data for the sunburst chart
        mycursor.execute("""
            SELECT 
                CONCAT(M.Emp_Fname, ' ', M.Emp_Lnamel) AS MANAGERNAME,
                D.Dept_Name AS DEPARTMENT,
                CONCAT(E.Emp_Fname, ' ', E.Emp_Lnamel) AS EMPLOYEENAME
            FROM LGDEPARTMENT D
            JOIN LGEMPLOYEE E ON D.Dept_Num = E.Dept_Num
            LEFT JOIN LGEMPLOYEE M ON D.Emp_Num = M.Emp_Num
            WHERE D.Dept_Name IN ('Accounting', 'Purchasing', 'Sales')
        """)
        hierarchy_data = pd.DataFrame(mycursor.fetchall(), columns=["MANAGERNAME", "DEPARTMENT", "EMPLOYEENAME"])

        # Create sunburst chart with custom colors and white text
        sunburst_fig = px.sunburst(
            hierarchy_data,
            path=["DEPARTMENT", "MANAGERNAME", "EMPLOYEENAME"],  # Define hierarchy
            title="Departments, Managers, and Employees",
            color="DEPARTMENT",  # Color based on department
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        # Update text color to white
        sunburst_fig.update_traces(textfont_color="white")  # Make all text white

        # Display sunburst chart
        st.plotly_chart(sunburst_fig, use_container_width=True)

        # Manager Data Table - Collapsible
        with st.expander("Manager Data"):
            # Ensure columns are in the correct order: Manager Name, Department Name, Employee Name
            st.dataframe(
                hierarchy_data[["MANAGERNAME", "DEPARTMENT", "EMPLOYEENAME"]].style.format(
                    {"MANAGERNAME": str, "DEPARTMENT": str, "EMPLOYEENAME": str}
                )
            )

    # Column 2: Top N Employees Chart
    with col2:
        st.subheader("Top N Employees")

        # Slider for user to select N
        top_n = st.slider("How many top employees?", min_value=1, max_value=20, value=10)  # Default is 10

        # Fetch data for the Top N Employees chart
        mycursor.execute(f"""
            SELECT 
                CONCAT(E.Emp_Fname, ' ', E.Emp_Lnamel) AS EMPLOYEENAME,
                SUM(LGInvoice.Inv_Total) AS Revenue,
                E.Emp_Num AS employee_ID
            FROM LGEMPLOYEE E
            JOIN LGInvoice ON E.Emp_Num = LGInvoice.Employee_ID
            GROUP BY EMPLOYEENAME, employee_ID
            ORDER BY Revenue DESC
            LIMIT {top_n}
        """)
        top_employees_data = pd.DataFrame(mycursor.fetchall(), columns=["EMPLOYEENAME", "Revenue", "employee_ID"])

        # Define custom colors matching the image
        custom_colors = [
            "#5DADEC",  # Light Blue
            "#2C7BB6",  # Blue
            "#FBB4AE",  # Pink
            "#F28E82",  # Red
            "#76C893",  # Light Green
            "#FDD835",  # Yellow
            "#D95F02",  # Orange
            "#AB82FF",  # Purple
            "#CD5C5C",  # Coral
            "#98FB98"   # Pale Green
        ]

        # Create bar chart for Top N Employees
        bar_chart = px.bar(
            top_employees_data,
            x="EMPLOYEENAME",
            y="Revenue",
            title="Top N Employees",
            color="Revenue",
            color_continuous_scale=custom_colors[:top_n],  # Match colors to number of employees
        )

        # Update bar chart layout
        bar_chart.update_traces(marker=dict(line=dict(color="black", width=0.5)))  # Add thin border to bars
        bar_chart.update_layout(
            xaxis_title="EMPLOYEENAME",
            yaxis_title="Revenue",
            legend_title="Revenue",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white"),
        )

        # Display bar chart
        st.plotly_chart(bar_chart, use_container_width=True)

        # Employee Data Table - Collapsible
        with st.expander("Employee Data"):
            st.dataframe(
                top_employees_data.style.format({"Revenue": "{:,.2f}", "employee_ID": "{:,.0f}"})  # Format with commas
            )





