import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class SeleniumExample {
    public static void main(String[] args) {
        // Set the path to the ChromeDriver (adjust this path as per your system)
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");

        // Instantiate the WebDriver
        WebDriver driver = new ChromeDriver();

        // Open a webpage
        driver.get("https://example.com");

        // Find an element by its ID and click it (e.g., clicking a button)
        WebElement button = driver.findElement(By.id("buttonId"));
        button.click();

        // Find an element by name and send keys (e.g., filling out a form)
        WebElement inputField = driver.findElement(By.name("username"));
        inputField.sendKeys("testuser");

        // Submit the form by finding the submit button and clicking it
        WebElement submitButton = driver.findElement(By.name("submit"));
        submitButton.click();

        // Close the browser after a short wait
        try {
            Thread.sleep(2000); // wait for 2 seconds
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // Close the browser
        driver.quit();
    }
}
